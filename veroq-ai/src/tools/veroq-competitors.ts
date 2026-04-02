import { tool } from "ai";
import { z } from "zod";
import { VeroqClient } from "@veroq/sdk";

export const veroqCompetitors = (options: { apiKey?: string } = {}) =>
  tool({
    description:
      "Get the competitive landscape for a ticker. Returns competitors with comparative sentiment, coverage volume, and sector positioning.",
    parameters: z.object({
      symbol: z
        .string()
        .describe("Ticker symbol to get competitors for (e.g. NVDA)"),
    }),
    execute: async ({ symbol }) => {
      const client = new VeroqClient({ apiKey: options.apiKey });
      return client.competitors(symbol);
    },
  });
