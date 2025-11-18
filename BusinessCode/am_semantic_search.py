# am_semantic_search.py
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Iterable, List, Dict, Tuple, Optional, Callable
from decimal import Decimal
from datetime import datetime
import json
from sqlalchemy import select, LargeBinary, Column
from loguru import logger

# ------- 可选：小型预训练模型（句向量），缺失则退化为 TF-IDF -------
_EMB_MODEL = None
_VECT_BACKEND = "sbert"  # "sbert" | "tfidf"
_FAISS = None


def _try_load_embedder(model_name: str | None = None):
    """尽力载入小模型；失败则返回 None（退化为 TFIDF）。"""
    global _EMB_MODEL, _VECT_BACKEND, _FAISS
    if _EMB_MODEL is not None:
        return
    try:
        from sentence_transformers import SentenceTransformer
        import faiss  # type: ignore
        _FAISS = faiss
        name = model_name or "paraphrase-multilingual-MiniLM-L12-v2"  # 体积小、通用
        _EMB_MODEL = SentenceTransformer(name)
        _VECT_BACKEND = "sbert"
    except Exception:
        # 退化方案：TF-IDF（仍能覆盖所有字段的词匹配）
        _EMB_MODEL = None
        _VECT_BACKEND = "tfidf"


def _to_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, (int, float, Decimal)):
        return str(x)
    if isinstance(x, (datetime,)):
        return x.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(x, (list, tuple, set)):
        return "、".join(_to_text(v) for v in x)
    if isinstance(x, dict):
        try:
            return json.dumps(x, ensure_ascii=False)
        except Exception:
            return str(x)
    return str(x)


from sqlalchemy.inspection import inspect as sqla_inspect


def _is_empty_scalar(v) -> bool:
    # 注意：0/False 不是空；None/"" 才是空
    return v is None or (isinstance(v, str) and v.strip() == "")


def _collect_field_names(row) -> List[str]:
    """
    返回 orm.py 中定义的“变量名”（映射属性名），不返回物理列名。
    自动排除二进制类型字段（LargeBinary/BLOB/BINARY/VARBINARY 等）
    或当前值为 bytes/bytearray/memoryview 的属性。
    """
    names: list[str] = []

    # --- ORM 实例：只拿映射的列属性名（column_attrs） ---
    try:
        if hasattr(row, "__mapper__"):
            insp = sqla_inspect(row)
            binary_keys: set[str] = set()

            # 标记哪些映射属性对应二进制列
            for prop in insp.mapper.column_attrs:
                is_binary = False
                # ColumnProperty 可能绑定多个 Column，这里任一为二进制即排除
                for col in getattr(prop, "columns", []) or []:
                    try:
                        t = col.type
                        tname = type(t).__name__.upper()
                        if isinstance(t, LargeBinary) or "BLOB" in tname or "BINARY" in tname:
                            is_binary = True
                            break
                    except Exception:
                        pass
                if is_binary:
                    binary_keys.add(prop.key)

            # 仅收集 column_attrs 的 key，且过滤掉二进制
            for prop in insp.mapper.column_attrs:
                k = prop.key
                if k not in binary_keys:
                    names.append(k)

            # 直接返回（已是 ORM 变量名集合）
            # 去重保持顺序
            seen = set()
            out = []
            for n in names:
                if n and n not in seen:
                    seen.add(n)
                    out.append(n)
            return out
    except Exception:
        pass

    # --- 非 ORM 对象（降级处理）：从 __dict__ 取属性名并按值类型过滤二进制 ---
    try:
        for k, v in vars(row).items():
            if k.startswith("_"):
                continue
            if isinstance(v, (bytes, bytearray, memoryview)):
                continue
            names.append(k)
    except Exception:
        pass

    # 去重保持顺序
    seen = set()
    out = []
    for n in names:
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return out


def _row_to_blob(row, field_names: list[str] | None = None) -> str:
    """
    把一条记录转成覆盖“尽可能多字段”的文本：
    'am_id: 123 | am_name: 250-3航爆弹 | country: 中国 | ...'
    """
    parts: list[str] = []

    # 若未指定字段名，则自动收集
    if not field_names:
        field_names = _collect_field_names(row)

    logger.debug(f"field_names={field_names}")

    # 逐字段取值（0/False 也要保留）
    for name in field_names:
        try:
            val = getattr(row, name, None)
        except Exception:
            val = None
        if _is_empty_scalar(val):
            continue
        txt = _to_text(val)
        if txt != "":
            parts.append(f"{name}: {txt}")

    # 兜底：至少把 id / name 放进去，避免空语料
    if not parts:
        # 常见主键和名称字段尝试若干别名
        for n in ("am_id", "id", "AMID", "AmID"):
            if hasattr(row, n):
                parts.append(f"{n}: {_to_text(getattr(row, n))}")
                break
        for n in ("am_name", "official_name", "chinese_name", "name", "AMName"):
            if hasattr(row, n):
                parts.append(f"{n}: {_to_text(getattr(row, n))}")
                break
        # 如果还是没有，作为最后兜底给出 repr
        if not parts:
            parts.append(repr(row))

    return " | ".join(parts)


@dataclass
class SemanticIndex:
    """内存向量索引；可从 domain 或 ORM 构建；覆盖所有字段。"""
    ids: List[int]
    backend: str  # "sbert" | "tfidf"
    model_name_or_dir: Optional[str] = None  # sbert 查询时需要编码
    # sbert
    faiss_index: Any | None = None
    # tfidf
    tfidf: Any | None = None
    tfidf_mat: Any | None = None

    @staticmethod
    def build(items: List[Tuple[int, str]], prefer_model: Optional[str] = None) -> "SemanticIndex":
        logger.debug("开始构建SemanticIndex")
        _try_load_embedder(prefer_model)
        ids = [i for i, _ in items]
        blobs = [(b or "").strip() for _, b in items]

        # —— 语料清洗：避免全空行导致空词表 ——
        # 若某条为空，填入一个极简占位符，防止 fit 时全空
        safe_blobs = [x if x != "" else "NA" for x in blobs]
        # logger.debug(f"safe_blobs={safe_blobs}")

        if _VECT_BACKEND == "sbert":
            logger.debug(f"_VECT_BACKEND为sbert")
            import numpy as np
            mat = _EMB_MODEL.encode(safe_blobs, normalize_embeddings=True).astype("float32")  # type: ignore
            dim = mat.shape[1]
            faiss = _FAISS
            index = faiss.IndexFlatIP(dim)
            index.add(mat)
            return SemanticIndex(ids=ids, backend="sbert", faiss_index=index)

        # ---------- TF-IDF （中文友好 & 兜底）----------
        # 使用 char_wb n-gram 对中文更稳，不依赖分词；不会触发“空词表”
        from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
        try:
            logger.debug("使用char_wb")
            vec = TfidfVectorizer(
                analyzer="char_wb",  # 以字符 n-gram 为单位（适配中文）
                ngram_range=(2, 4),  # 2~4 字片段
                min_df=1,
                max_features=60000,
                # stop_words=None  # 中文不设停用词
            )
            mat = vec.fit_transform(safe_blobs)
            return SemanticIndex(ids=ids, backend="tfidf", tfidf=vec, tfidf_mat=mat)
        except ValueError:
            logger.debug("使用char")
            # 兜底 1：退成 char 级别
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
            vec = TfidfVectorizer(
                analyzer="char",
                ngram_range=(1, 3),
                min_df=1,
                max_features=60000,
            )
            mat = vec.fit_transform(safe_blobs)
            return SemanticIndex(ids=ids, backend="tfidf", tfidf=vec, tfidf_mat=mat)

    @staticmethod
    def load_index(path_base: str) -> "SemanticIndex":
        """
        从指定前缀加载索引（自动识别 sbert/tfidf）。
        会读取：
          - sbert: *.faiss + *.ids.json + *.meta.json
          - tfidf: *.tfidf.joblib
        """
        base = os.path.splitext(path_base)[0]
        faiss_path = base + ".faiss"
        tfidf_path = base + ".tfidf.joblib"

        # 尝试加载 sbert
        if os.path.exists(faiss_path):
            import faiss  # type: ignore
            with open(base + ".ids.json", "r", encoding="utf-8") as f:
                ids = json.load(f)
            meta = {"backend": "sbert", "model": None}
            meta_path = base + ".meta.json"
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            faiss_index = faiss.read_index(faiss_path)
            model = meta.get("model")
            return SemanticIndex(ids=ids, backend="sbert", model_name_or_dir=model, faiss_index=faiss_index)

        # 尝试加载 tfidf
        if os.path.exists(tfidf_path):
            try:
                import joblib  # type: ignore
            except Exception as e:
                raise RuntimeError("加载 TF-IDF 索引需要 joblib，请先安装：pip install joblib") from e
            data = joblib.load(tfidf_path)
            return SemanticIndex(ids=data["ids"], backend="tfidf", tfidf=data["vec"], tfidf_mat=data["mat"])

        raise FileNotFoundError(f"未找到索引文件：{faiss_path} 或 {tfidf_path}")

    def save_index(self, path_base: str) -> None:
        """
        保存索引文件到指定前缀：
        - sbert:  保存 path_base.faiss / path_base.ids.json / path_base.meta.json
        - tfidf:  保存 path_base.tfidf.joblib
        """
        base = os.path.splitext(path_base)[0]
        os.makedirs(os.path.dirname(base) or ".", exist_ok=True)

        if self.backend == "sbert":
            if self.faiss_index is None:
                raise RuntimeError("SBERT 索引缺少 faiss_index")
            import faiss  # type: ignore
            faiss.write_index(self.faiss_index, base + ".faiss")
            with open(base + ".ids.json", "w", encoding="utf-8") as f:
                json.dump(self.ids, f, ensure_ascii=False)
            with open(base + ".meta.json", "w", encoding="utf-8") as f:
                json.dump(
                    {"backend": "sbert", "model": self.model_name_or_dir},
                    f,
                    ensure_ascii=False,
                )
            return

        # TF-IDF
        try:
            import joblib  # type: ignore
        except Exception as e:
            raise RuntimeError("保存 TF-IDF 索引需要 joblib，请先安装：pip install joblib") from e
        joblib.dump({"vec": self.tfidf, "mat": self.tfidf_mat, "ids": self.ids}, base + ".tfidf.joblib")

    def search(self, query: str, topk: int = 100) -> List[int]:
        q = query.strip()
        logger.debug(f"query: {q}")
        if not q:
            return self.ids[:topk]

        logger.debug(f"self.backend={self.backend}")
        if self.backend == "sbert":
            import numpy as np
            qv = _EMB_MODEL.encode([q], normalize_embeddings=True).astype("float32")  # type: ignore
            D, I = self.faiss_index.search(qv, min(topk, len(self.ids)))  # type: ignore
            return [self.ids[i] for i in I[0]]
        else:
            from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
            qv = self.tfidf.transform([q])  # type: ignore
            sims = cosine_similarity(qv, self.tfidf_mat)[0]  # type: ignore
            order = sims.argsort()[::-1][:topk]
            return [self.ids[i] for i in order]


# --------- 构建索引（覆盖所有字段） ----------
def build_semantic_index_from_db(session, orm_cls, id_attr: str = "am_id",
                                 prefer_model: str | None = None) -> Optional[SemanticIndex]:
    """
    从数据库加载所有 ORM 行，自动拼“覆盖全部字段”的 blob，建立内存索引
    """
    stmt = select(orm_cls)
    rows = session.execute(stmt).scalars().all()
    if len(rows) == 0:
        return None
    items: List[Tuple[int, str]] = []
    for r in rows:
        rid = getattr(r, id_attr)
        blob = _row_to_blob(r)  # 全字段
        # logger.debug(f"_row_to_blob={blob}")
        items.append((rid, blob))
    return SemanticIndex.build(items, prefer_model=prefer_model)


def build_semantic_index_from_items(items: List[Any], id_getter: Callable[[Any], int],
                                    prefer_model: str | None = None) -> SemanticIndex:
    pairs: List[Tuple[int, str]] = [(id_getter(x), _row_to_blob(x)) for x in items]
    return SemanticIndex.build(pairs, prefer_model=prefer_model)


# --------- 语义检索 + 复用组合检索（可选过滤） ----------
def smart_query(session, idx: SemanticIndex, query: str,
                combine_filter: Optional[Callable[[Any, Dict[str, Any]], List[Any]]] = None,
                to_condition: Optional[Callable[[str], Dict[str, Any]]] = None,
                topk: int = 200) -> List[Any]:
    """
    先用“全字段语料”的语义召回，再（可选）用你已有的组合检索过滤。
    - combine_filter: 形如 your _query_ammunition_by_conditions(session, condition)
    - to_condition:   把自然语言 query → 你已有的 condition_data
    """
    cand_ids = idx.search(query, topk=topk)
    logger.debug(f"cand_ids: {cand_ids}")

    # 若不做结构化过滤，直接返回 ID 子集对应的记录
    from sqlalchemy import select
    # 这里默认 ORM 类为 AmmunitionORM；你可在外层部分函数封装
    from am_models import AmmunitionORM, Ammunition
    stmt = select(AmmunitionORM).where(AmmunitionORM.am_id.in_(cand_ids))
    orm_rows = session.execute(stmt).scalars().all()

    if combine_filter and to_condition:
        condition = to_condition(query)
        # 你的过滤函数通常返回 List[Ammunition]
        filtered = combine_filter(session, condition)
        # 与 cand_ids 取交集（如果过滤函数没限定 id 子集）
        by_id = {a.am_id: a for a in filtered}
        return [by_id[i] for i in cand_ids if i in by_id]

    # 默认：直接把 ORM 转成领域对象（若你用的是 Pydantic，可 from_orm）
    results = [Ammunition.from_orm(r) if hasattr(Ammunition, "from_orm") else r for r in orm_rows]
    # 按 cand_ids 顺序返回
    by_id = {getattr(x, "am_id"): x for x in results}
    return [by_id[i] for i in cand_ids if i in by_id]
