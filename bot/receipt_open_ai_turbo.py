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
                            # "text": f"""You are an AI that extracts product names and prices from receipt text. 
                            #     The text is in finnish. You also need to shorten long product names to a short one 
                            #     that conveys the essence, and figure out which words were shortened, for example: 
                            #     'kirsikkatomatti' instead of 'Luumukirsikkatomatti', 'kanan jauheliha' instead of 'Kanamestari kanan jauhel',
                            #     'kaurajuoma' instead of 'Vemondo luomu kaurajuoma'.
                            #     There also will be some products, which names are difficult to recognize - leave them as they are. 
                            #     Exampe: "Vemondo Luomu mantelij. sokt"
                            #     Under the product names, it can be written how many servings of the product were purchased at what price, 
                            #     for example: 3 x 2,95 EUR
                            #     The price is where there is a designation EUR or €. 
                            #     You should give me the price for the total ammount of product, in the above example it is 8,85.
                            #     If underneath the product there's an information about discount, you should return the product price considering the discount.
                            #     Return the data as a JSON array of products with their prices, like this:
                            #     [{{'name': "Product1", "price": 9.99}}, {{"name": "Product2", "price": 4.50}}]
                            #     Don't give me any additional information, text, formating, just the JSON array
                            "text": f"""You are an AI that extracts product entries from receipt text in Finnish and returns a strict 
                                JSON array ONLY. The receipt text may contain product names, quantities, per-unit prices, 
                                totals, discounts, and currency markers (EUR or €). Do exactly what follows — nothing else.

                                Rules:
                                1. Output: a single JSON array and nothing else. Use double quotes for strings. Each product is an object with these fields:
                                - "name": short normalized product name (string).
                                - "price": total price paid for that product after discounts (number).

                                Example item: {{"name":"kaurajuoma","price":2.49}}

                                2. Name normalization:
                                - Make names short but meaningful (essence of the product). Use lowercase, remove brand/marketing tokens if they are not essential (e.g., "Vemondo Luomu kaurajuoma" -> "kaurajuoma", "Luumukirsikkatomatti" -> "kirsikkatomatti").
                                - If you remove words, list them in "shortened_from". If you cannot confidently shorten the name, set "name" equal to the original and set "shortened_from": null (or omit "shortened_from").

                                3. Prices and numbers:
                                - Recognize prices with "EUR" or "€" and decimal commas (convert commas to dots). Output numeric values (not strings).
                                - If a line shows quantity, e.g. "3 x 2,95 EUR" or "3 x 2.95€", compute total = 3 * 2.95 and use that (8.85).
                                - If a product has a line with a total price already (e.g., "8,85 EUR" under the product), use that.
                                - Round prices to two decimal places using normal rounding.

                                4. Discounts:
                                - If there is a discount line immediately after (or directly beneath) the product, e.g. "-0,50 EUR", "ALENNUS -0,50", or similar, subtract it from the product's price.
                                - If discount appears as percentage on the same product line, apply it.
                                - If discount is global and not attributable to a specific product, ignore it (do not alter product prices) unless the receipt text explicitly ties it to a product line.

                                5. Ambiguities:
                                - If a product name is garbled or you cannot identify what to shorten, keep the original text verbatim in "name" and set "shortened_from": null or omit that field.
                                - Preserve order of lines but output does not need to preserve receipt order.

                                6. Strict formatting:
                                - The response must be exactly the JSON array (single top-level array). No extra commentary, no code fences, no explanations.

                                Examples:

                                Input lines:
                                "Vemondo Luomu kaurajuoma 1l
                                1 x 2,95 EUR
                                MUSTA ALENNUS -0,50 EUR
                                Kanan jauheliha 400g
                                2 x 3,50 EUR
                                Luumukirsikkatomatti 0,5kg
                                1 x 2,20 EUR"

                                Expected JSON output:
                                [
                                {{"name":"kaurajuoma","price":2.45}},
                                {{"name":"kanan jauheliha","price":7.00}},
                                {{"name":"kirsikkatomatti","price":2.20}}
                                ]

                                Do not include any additional text outside the JSON array.
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