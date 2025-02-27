import os
import sys
import click
from alembic import command
from alembic.config import Config

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def get_alembic_config():
    """获取 Alembic 配置"""
    config = Config(os.path.join(BASE_DIR, "alembic.ini"))
    config.set_main_option("script_location", os.path.join(BASE_DIR, "alembic"))
    return config

@click.group()
def cli():
    """数据库迁移命令行工具"""
    pass

@cli.command()
def init():
    """初始化迁移环境"""
    config = get_alembic_config()
    command.init(config, "alembic")
    click.echo("迁移环境初始化完成")

@cli.command()
@click.option('--message', '-m', help='迁移说明')
def migrate(message):
    """生成新的迁移脚本"""
    config = get_alembic_config()
    command.revision(config, message=message, autogenerate=True)
    click.echo("迁移脚本生成完成")

@cli.command()
def upgrade():
    """升级数据库到最新版本"""
    config = get_alembic_config()
    command.upgrade(config, "head")
    click.echo("数据库升级完成")

@cli.command()
@click.argument('revision', default="-1")
def downgrade(revision):
    """回滚数据库版本"""
    config = get_alembic_config()
    command.downgrade(config, revision)
    click.echo(f"数据库已回滚到版本: {revision}")

if __name__ == '__main__':
    cli() 