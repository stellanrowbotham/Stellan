// Data access for the public API. The API's database user can only call these three functions
// (see migration 0008), so this file is the whole surface.

export interface IntakeResult {
  lead_id: string;
  duplicate: boolean;
  needs_human: boolean;
  suppressed: boolean;
}

export interface Store {
  hitRateLimit(bucket: string, limit: number, windowSeconds: number): Promise<boolean>;
  intakeLead(payload: Record<string, unknown>): Promise<IntakeResult>;
  processUnsubscribe(email: string | null, phone: string | null, source: string): Promise<{ cancelled_messages: number }>;
  ping(): Promise<boolean>;
}

// Minimal shape of a `postgres` (porsager) client, so this file has no runtime import and works on Node and Deno.
// Adapters pass their client with `as unknown as SqlClient`.
export type SqlClient = {
  <T = Record<string, unknown>>(strings: TemplateStringsArray, ...values: unknown[]): PromiseLike<T[]>;
  json(value: unknown): unknown;
};

export function createPgStore(sql: SqlClient): Store {
  return {
    async hitRateLimit(bucket, limit, windowSeconds) {
      const [row] = await sql<{ ok: boolean }>`select growth.hit_rate_limit(${bucket}, ${limit}, ${windowSeconds}) as ok`;
      return row.ok;
    },
    async intakeLead(payload) {
      const [row] = await sql<{ r: IntakeResult }>`select growth.intake_lead(${sql.json(payload)}::jsonb) as r`;
      return row.r;
    },
    async processUnsubscribe(email, phone, source) {
      const [row] = await sql<{ r: { cancelled_messages: number } }>`select growth.process_unsubscribe(${email}, ${phone}, ${source}) as r`;
      return row.r;
    },
    async ping() {
      try {
        await sql`select 1`;
        return true;
      } catch {
        return false;
      }
    },
  };
}
