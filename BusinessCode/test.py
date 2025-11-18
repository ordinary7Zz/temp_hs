import bcrypt  # 直接导入底层库，验证是否能正常加载

# 测试 passlib 能否调用 bcrypt
from passlib.hash import bcrypt as passlib_bcrypt

hashed_password = bcrypt.hashpw('aaa'.encode("utf-8"),bcrypt.gensalt() )
#hashed_password = bcrypt.hash("111")  # 生成哈希
print("生成Bcrypt密码", hashed_password)
print("加密结果:", hashed_password.decode("utf-8"))  # 转为字符串存储]
