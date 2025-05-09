from dotenv import load_dotenv
import logging
import os
from openai import OpenAI

success = load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_TOKEN"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def image_recognition_turbo(base64_image):

    try:
        logger.info(f"Receipt recognition launched")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""You will be given a receipt photo and need to recognize it and return the text. 
                                The receipt is in finnish. 
                                Under the product names, it can be written how many servings of the product were purchased at what price, 
                                for example: 3 x 2,95 EUR
                                The price is where there is a designation EUR or €. 
                                When returning the text, follow the lines as in the original image - 
                                the price should be on the same line as the product.
                                Don't give me any additional information, text, formating, just the receipt text"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
        )

    except Exception as e:
        logger.error(f"Product identifing with OpenAI failed: {e}")
        return None

    return completion.choices[0].message.content


def product_recognition_turbo(recognized_image):

    try:
        logger.info(f"Product identifing launched")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""You are an AI that extracts product names and prices from receipt text. 
                                The text is in finnish. You also need to shorten long product names to a short one 
                                that conveys the essence, and figure out which words were shortened, for example: 
                                'kirsikkatomatti' instead of 'Luumukirsikkatomatti', 'kanan jauheliha' instead of 'Kanamestari kanan jauhel',
                                'kaurajuoma' instead of 'Vemondo luomu kaurajuoma'.
                                There also will be some products, which names are difficult to recognize - leave them as they are. 
                                Exampe: "Vemondo Luomu mantelij. sokt"
                                Under the product names, it can be written how many servings of the product were purchased at what price, 
                                for example: 3 x 2,95 EUR
                                The price is where there is a designation EUR or €. 
                                You should give me the price for the total ammount of product, in the above example it is 8,85.
                                If underneath the product there's an information about discount, you should return the product price considering the discount.
                                Return the data as a JSON array of products with their prices, like this:
                                [{{'name': "Product1", "price": 9.99}}, {{"name": "Product2", "price": 4.50}}]
                                Don't give me any additional information, text, formating, just the JSON array
                                """
                        },
                        {
                            "type": "text",
                            "text": f"{recognized_image}",
                        },
                    ],
                }
            ],
        )

    except Exception as e:
        logger.error(f"Product identifing with OpenAI failed: {e}")
        return None

    return completion.choices[0].message.content