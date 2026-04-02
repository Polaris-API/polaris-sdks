import { tool } from "ai";
import { z } from "zod";
import { VeroqClient } from "@veroq/sdk";

export const veroqTrending = (options: { apiKey?: string } = {}) =>
  tool({
    description:
      "Get trending entities across the news — the people, companies, and topics generating the most coverage right now.",
    parameters: z.object({
      limit: z
        .number()
        .optional()
        .describe("Max entities to return (default 10)"),
    }),
    execute: async ({ limit }) => {
      const client = new VeroqClient({ apiKey: options.apiKey });
      return client.trendingEntities(limit);
    },
  });
