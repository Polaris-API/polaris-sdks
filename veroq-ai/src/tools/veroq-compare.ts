import { tool } from "ai";
import { z } from "zod";
import { VeroqClient } from "@veroq/sdk";

export const veroqCompare = (options: { apiKey?: string } = {}) =>
  tool({
    description:
      "Compare how different news outlets covered the same story. Shows framing, bias, and what each side emphasizes or omits.",
    parameters: z.object({
      briefId: z
        .string()
        .describe("The brief ID to compare source coverage for"),
    }),
    execute: async ({ briefId }) => {
      const client = new VeroqClient({ apiKey: options.apiKey });
      return client.compareSources(briefId);
    },
  });
