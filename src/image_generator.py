import time

MAX_RETRIES = 50

def generate_with_retry(prompt):

    for attempt in range(MAX_RETRIES):

        try:
            image = generate_image(prompt)
            return image

        except Exception as e:

            error = str(e).lower()

            if "quota" in error or "rate" in error or "429" in error:

                print("Rate limit reached...")
                time.sleep(60)

                continue

            raise

    raise Exception("Retries exhausted")