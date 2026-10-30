import "dotenv/config";
import { browserbase, Stagehand } from "@browserbasehq/stagehand";
import { z } from "zod/v4";

const PRODUCT_URL =
  "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html";

async function main() {
  const apiKey = process.env.BROWSERBASE_API_KEY;
  if (!apiKey) {
    throw new Error("BROWSERBASE_API_KEY is required");
  }

  const browser = await browserbase.launch({ apiKey });
  console.log(`Session: https://www.browserbase.com/sessions/${browser.sessionId}`);

  try {
    const stagehand = await Stagehand.create({ browser });

    try {
      const [page] = await browser.context.pages();
      if (!page) {
        throw new Error("No page was created for the browser session");
      }

      console.log("Navigating to the product page…");
      await page.goto(PRODUCT_URL, { waitUntil: "domcontentloaded" });

      console.log("Extracting product details…");
      const result = await stagehand.extract(
        "Extract the book's title, price, star rating (1-5), stock availability, and the first sentence of its product description.",
        z.object({
          title: z.string(),
          price: z.string(),
          rating: z.number(),
          availability: z.string(),
          description: z.string(),
        })
      );
      // The rating is only in a CSS class (e.g. "star-rating Three"), so read it directly.
      const ratingWord = await page.evaluate(
        "document.querySelector('.product_main .star-rating')?.className.split(' ')[1] ?? ''"
      );
      const words: Record<string, number> = { One: 1, Two: 2, Three: 3, Four: 4, Five: 5 };
      console.log("Product:\n", { ...result.data, rating: words[String(ratingWord)] ?? null });
    } finally {
      await stagehand.close();
    }
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
