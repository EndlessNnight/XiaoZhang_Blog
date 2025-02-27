import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from datetime import datetime, timedelta
from ..core.config import settings

# 存储验证码
verification_codes = {}

async def send_verification_email(email: str) -> dict:
    """发送验证码邮件"""
    # 生成6位验证码
    code = ''.join(random.choices(string.digits, k=6))
    
    # 存储验证码和过期时间(10分钟)
    verification_codes[email] = {
        'code': code,
        'expires_at': datetime.now() + timedelta(minutes=10)
    }
    
    message = MIMEMultipart()
    message["From"] = settings.EMAIL_USER
    message["To"] = email
    message["Subject"] = "小张博客 - 邮箱验证码"
    
    body = f"""
    <html>
        <body>
            <p>您好！</p>
            <p>您的验证码是: <strong>{code}</strong></p>
            <p>验证码有效期为10分钟。</p>
            <p>如果这不是您的操作，请忽略此邮件。</p>
        </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))
    
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_USER,
            password=settings.EMAIL_PASSWORD,
            use_tls=True
        )
        return {"message": "验证码已发送"}
    except Exception as e:
        raise Exception(f"发送邮件失败: {str(e)}")

def verify_code(email: str, code: str) -> bool:
    """验证邮箱验证码"""
    if email not in verification_codes:
        return False
    
    stored = verification_codes[email]
    if datetime.now() > stored['expires_at']:
        del verification_codes[email]
        return False
    
    if stored['code'] != code:
        return False
    
    del verification_codes[email]
    return True 