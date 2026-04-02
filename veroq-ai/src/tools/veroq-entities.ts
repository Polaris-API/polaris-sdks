import { tool } from "ai";
import { z } from "zod";
import { VeroqClient } from "@veroq/sdk";

export const veroqEntities = (options: { apiKey?: string } = {}) =>
  tool({
    description:
      "Look up news coverage for a specific entity (company, person, technology).",
    parameters: z.object({
      name: z
        .string()
        .describe(
          "Entity name to look up (e.g. OpenAI, Elon Musk, quantum computing)"
        ),
    }),
    execute: async ({ name }) => {
      const client = new VeroqClient({ apiKey: options.apiKey });
      return client.entityBriefs(name);
    },
  });
