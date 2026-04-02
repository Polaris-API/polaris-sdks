import { tool } from "ai";
import { z } from "zod";
import { VeroqClient } from "@veroq/sdk";

export const veroqBrief = (options: { apiKey?: string } = {}) =>
  tool({
    description:
      "Get a specific verified news brief by ID with full analysis, sources, and counter-arguments.",
    parameters: z.object({
      id: z.string().describe("The brief ID to retrieve"),
    }),
    execute: async ({ id }) => {
      const client = new VeroqClient({ apiKey: options.apiKey });
      return client.brief(id);
    },
  });
