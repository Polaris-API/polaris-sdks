import { tool } from "ai";
import { z } from "zod";
import { VeroqClient } from "@veroq/sdk";

export const veroqTimeline = (options: { apiKey?: string } = {}) =>
  tool({
    description:
      "Get the story evolution timeline for a living brief — shows how coverage developed over time with versioned updates, confidence changes, and new sources.",
    parameters: z.object({
      briefId: z.string().describe("Brief ID"),
    }),
    execute: async ({ briefId }) => {
      const client = new VeroqClient({ apiKey: options.apiKey });
      return client.timeline(briefId);
    },
  });
