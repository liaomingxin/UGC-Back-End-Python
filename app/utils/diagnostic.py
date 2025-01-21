from pathlib import Path
import json
import time
from datetime import datetime
from typing import Dict, Any
import yaml

class CrawlerDiagnostic:
    """
    爬虫诊断工具类，用于记录爬虫的详细运行信息。
    """
    def __init__(self):
        self.diagnostic_dir = Path("logs/diagnostic")
        self.diagnostic_dir.mkdir(parents=True, exist_ok=True)
        
    def log_crawl_attempt(self, url: str, site_config: Dict[str, Any], html_snapshot: str = None) -> str:
        """
        记录一次爬取尝试的详细信息。
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"crawl_{timestamp}"
        
        # 创建会话目录
        session_dir = self.diagnostic_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        # 记录基本信息
        info = {
            "timestamp": timestamp,
            "url": url,
            "site_config": site_config,
            "user_agent": "Chrome/132.0.6834.84"  # 从配置中获取
        }
        
        # 保存配置信息
        with open(session_dir / "info.yml", "w", encoding="utf-8") as f:
            yaml.dump(info, f, allow_unicode=True)
            
        # 保存HTML快照（如果有）
        if html_snapshot:
            with open(session_dir / "snapshot.html", "w", encoding="utf-8") as f:
                f.write(html_snapshot)
                
        return session_id
    
    def log_element_state(self, session_id: str, element_type: str, 
                         selector: str, found: bool, value: str = None, error: str = None):
        """
        记录元素查找和提取的状态。
        """
        log_file = self.diagnostic_dir / session_id / "elements.log"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "element_type": element_type,
            "selector": selector,
            "found": found,
            "value": value,
            "error": error
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    def log_extraction_result(self, session_id: str, success: bool, 
                            product_data: Dict[str, Any] = None, error: str = None):
        """
        记录最终的提取结果。
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "product_data": product_data,
            "error": error
        }
        
        with open(self.diagnostic_dir / session_id / "result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2) 