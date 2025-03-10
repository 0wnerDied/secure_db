"""
测试数据导入导出功能
"""

import os
import sys
import logging
import random
from test_config import PROJECT_ROOT, TEST_DATA_CONFIG

# 添加项目根目录到Python路径
sys.path.insert(0, str(PROJECT_ROOT))

# 导入项目模块
try:
    from core.secure_db import SecureDB
    from generate_test_data import generate_privacy_test_data
except ImportError as e:
    logger = logging.getLogger("数据导入导出测试")
    logger.error(f"导入项目模块失败: {e}")
    logger.error("请确保项目结构正确，并且已安装所有依赖")
    sys.exit(1)

logger = logging.getLogger("数据导入导出测试")


def test_export_import():
    """测试数据导出和导入功能"""
    logger.info("开始测试数据导出和导入功能...")
    success = True

    try:
        # 初始化安全数据库系统
        secure_db = SecureDB(load_keys=True)

        # 生成测试记录
        test_records = []
        record_ids = []

        logger.info("生成测试记录...")
        for _ in range(10):
            customer_id = random.randint(*TEST_DATA_CONFIG["index_range"])
            data = generate_privacy_test_data(customer_id)
            record_id = secure_db.add_record(customer_id, data, enable_range_query=True)
            record_ids.append(record_id)
            test_records.append(data)

        # 导出数据
        export_file = TEST_DATA_CONFIG["export_file"]
        logger.info(f"导出数据到文件: {export_file}")

        export_count = secure_db.export_records(record_ids, export_file)
        if export_count == len(record_ids):
            logger.info(f"成功导出 {export_count} 条记录")
        else:
            logger.error(
                f"导出失败，预期 {len(record_ids)} 条，实际导出 {export_count} 条"
            )
            success = False

        # 删除原记录
        logger.info("删除原始记录...")
        secure_db.delete_records_batch(record_ids)

        # 导入数据
        logger.info(f"从文件导入数据: {export_file}")
        import_result = secure_db.import_records(export_file)

        if import_result and len(import_result) == len(record_ids):
            logger.info(f"成功导入 {len(import_result)} 条记录")

            # 验证导入的数据
            logger.info("验证导入的数据...")
            for i, record_id in enumerate(import_result):
                imported_data = secure_db.get_record(record_id)
                original_data = test_records[i]

                if imported_data == original_data:
                    logger.debug(f"记录 {record_id} 验证成功")
                else:
                    logger.error(f"记录 {record_id} 验证失败，数据不匹配")
                    success = False

            # 清理导入的记录
            secure_db.delete_records_batch(import_result)
        else:
            logger.error(
                f"导入失败，预期 {len(record_ids)} 条，实际导入 {len(import_result) if import_result else 0} 条"
            )
            success = False

        # 清理导出文件
        if os.path.exists(export_file):
            os.remove(export_file)
            logger.info(f"已删除导出文件: {export_file}")

        if success:
            logger.info("数据导入导出测试通过")
        else:
            logger.error("数据导入导出测试失败")

        return success

    except Exception as e:
        logger.error(f"数据导入导出测试出现异常: {e}")
        return False


if __name__ == "__main__":
    success = test_export_import()
    sys.exit(0 if success else 1)
