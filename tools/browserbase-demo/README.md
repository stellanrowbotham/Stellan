# Browserbase demo: scrape a product page

Opens a real Chrome browser in Browserbase's cloud, goes to a book's page on
[books.toscrape.com](https://books.toscrape.com) (a site made for scraping practice), and pulls out
the title, price, star rating, stock and description with Stagehand.

## Run it
1. `cd tools/browserbase-demo && npm install` (needs Node.js 22.18+)
2. `cp .env.example .env` and put your key after `BROWSERBASE_API_KEY=`
   (from browserbase.com/settings). **Never commit `.env`**: this repo is public.
3. `npm start`, then open the `Session:` link it prints to watch the replay.

## Notes
- Runs on the Browserbase free plan. The AI step uses Model Gateway through the Browserbase key
  (free plan includes about $5 of tokens), so leave any other model key unset.
- The star rating is read from the page's CSS class, because the AI can't see star images.
- Change `PRODUCT_URL` and the `z.object({...})` fields in `index.ts` to scrape something else.
  Big retailers (Amazon, etc.) usually block free-plan browsers.
