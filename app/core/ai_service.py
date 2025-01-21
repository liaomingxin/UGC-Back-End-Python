from typing import Dict, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config.settings import settings
from app.models.schemas import (
    ProductDTO, 
    GenerateMimicRequest, 
    GenerateMimicResponse
)
from app.utils.logger import setup_logger

logger = setup_logger()

class AIService:
    """
    AI 服务类，用于与 OpenAI API 交互，生成营销文案。
    """

    def __init__(self):
        """
        初始化 AIService 实例。
        """
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_content(
        self, 
        product: ProductDTO, 
        style: str, 
        length: str, 
        language: str
    ) -> str:
        """
        调用 OpenAI API 生成营销文案内容。

        参数：
            product (ProductDTO): 商品信息。
            style (str): 文案风格。
            length (str): 文案长度。
            language (str): 文案语言。

        返回：
            str: 生成的文案内容。
        """
        try:
            prompt = self._build_content_prompt(product, style, length, language)
            request_body = {
                "model": "gpt-3.5-turbo",
                "stream": False,
                "temperature": 0.8,
                "messages": [
                    {"role": "system", "content": "你是一个专业的电商文案撰写专家，擅长创作吸引人的营销文案。"},
                    {"role": "user", "content": prompt}
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=request_body,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()
                generated_content = result["choices"][0]["message"]["content"]

                logger.info("Successfully generated content")
                return generated_content

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_mimic_content(
        self, 
        request: GenerateMimicRequest
    ) -> GenerateMimicResponse:
        """
        调用 OpenAI API 生成模仿风格的文案。

        参数：
            request (GenerateMimicRequest): 包含模板和要求的文案生成请求。

        返回：
            GenerateMimicResponse: 包含生成文案及分析结果的响应。
        """
        try:
            prompt = self._build_mimic_prompt(request)
            request_body = {
                "model": "gpt-3.5-turbo",
                "stream": False,
                "temperature": 0.7,
                "messages": [
                    {"role": "system", "content": "你是一个专业的文案创作专家，擅长模仿和创新。请基于用户提供的模板文案，结合场景和要求创作新的文案。"},
                    {"role": "user", "content": prompt}
                ]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=request_body,
                    timeout=30.0
                )

                response.raise_for_status()
                result = response.json()
                generated_content = result["choices"][0]["message"]["content"]

                word_count = len(generated_content)
                sentiment = self._analyze_sentiment(generated_content)
                keywords = self._extract_keywords(generated_content)

                return GenerateMimicResponse(
                    content=generated_content,
                    word_count=word_count,
                    sentiment=sentiment,
                    keywords=keywords
                )

        except Exception as e:
            logger.error(f"Error generating mimic content: {str(e)}")
            raise

    def _build_content_prompt(self, product: ProductDTO, style: str, length: str, language: str) -> str:
        """
        构建生成文案的提示信息。

        返回：
            str: 构建的提示信息。
        """
        return (
            f"你是一个专业的电商文案撰写专家。请根据以下要求创作一段商品推荐文案：\n\n"
            f"商品信息：\n"
            f"- 标题：{product.title}\n"
            f"- 价格：{product.price}\n\n"
            f"要求：\n"
            f"1. 文案风格：{self._get_style_description(style)}\n"
            f"2. 文案长度：{self._get_length_description(length)}\n"
            f"3. 使用语言：{self._get_language_description(language)}\n\n"
            f"注意事项：\n"
            f"1. 在文案中自然地插入这个链接标记：[LINK]\n"
            f"2. 在合适的位置插入图片标记：[IMAGE]\n"
            f"3. 突出商品特点和价格优势\n"
            f"4. 确保文案语言流畅，富有感染力\n"
            f"5. 适当使用emoji增加文案活力"
        )

    def _build_mimic_prompt(self, request: GenerateMimicRequest) -> str:
        """
        构建模仿文案的提示信息。

        返回：
            str: 构建的提示信息。
        """
        prompt = (
            f"请参考以下模板文案的风格和特点，创作一段新的营销文案：\n\n"
            f"模板文案：\n{request.template}\n\n"
            f"创作要求：\n"
            f"1. 场景：{request.scene}\n"
            f"2. 文案长度：{request.length}\n"
        )

        if request.product_info:
            prompt += (
                f"\n商品信息：\n"
                f"- 标题：{request.product_info.title}\n"
                f"- 价格：{request.product_info.price}\n"
            )

        prompt += (
            "\n注意事项：\n"
            "1. 保持原文案的风格特点\n"
            "2. 适当创新，避免完全照搬\n"
            "3. 确保文案流畅自然\n"
            "4. 突出商品卖点和价值\n"
        )

        return prompt

    def _analyze_sentiment(self, content: str) -> str:
        """
        简单情感分析。

        返回：
            str: 文案情感类型（positive/neutral/negative）。
        """
        positive_words = ["优秀", "完美", "出色", "惊艳", "超值"]
        negative_words = ["一般", "普通", "一般般"]

        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def _extract_keywords(self, content: str) -> List[str]:
        """
        提取关键词。

        返回：
            List[str]: 提取的关键词列表。
        """
        common_words = ["的", "了", "和", "与", "在", "是"]
        words = content.split()
        keywords = [w for w in words if len(w) > 1 and w not in common_words]
        return list(set(keywords))[:5]

    def _get_style_description(self, style: str) -> str:
        """
        获取文案风格描述。

        返回：
            str: 文案风格描述。
        """
        style_map = {
            "professional": "专业正式，突出商品价值和专业特性",
            "casual": "轻松随意，以朋友般的语气介绍商品",
            "humorous": "幽默诙谐，用轻松有趣的方式推荐商品",
            "elegant": "优雅格调，强调商品的品质与格调"
        }
        return style_map.get(style, "专业正式")

    def _get_length_description(self, length: str) -> str:
        """
        获取文案长度描述。

        返回：
            str: 文案长度描述。
        """
        length_map = {
            "short": "100字以内的简短文案",
            "medium": "200字左右的适中文案",
            "long": "300字以上的详细文案"
        }
        return length_map.get(length, "200字左右的适中文案")

    def _get_language_description(self, language: str) -> str:
        """
        获取文案语言描述。

        返回：
            str: 文案语言描述。
        """
        language_map = {
            "zh": "中文",
            "en": "英文",
            "jp": "日文"
        }
        return language_map.get(language, "中文")
