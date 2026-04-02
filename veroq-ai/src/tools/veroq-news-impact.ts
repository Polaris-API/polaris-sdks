import { tool } from "ai";
import { z } from "zod";
import { VeroqClient } from "@veroq/sdk";

export const veroqNewsImpact = (options: { apiKey?: string } = {}) =>
  tool({
    description:
      "Analyze the impact of news coverage on a ticker's price and sentiment. Shows how recent news events correlated with price movements.",
    parameters: z.object({
      symbol: z
        .string()
        .describe("Ticker symbol to analyze (e.g. NVDA)"),
    }),
    execute: async ({ symbol }) => {
      const client = new VeroqClient({ apiKey: options.apiKey });
      return client.newsImpact(symbol);
    },
  });
