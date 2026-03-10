-- AlterTable
ALTER TABLE "users" ALTER COLUMN "trust_score" SET DEFAULT 36.5,
ALTER COLUMN "trust_score" SET DATA TYPE DECIMAL(3,1);

ALTER TABLE "users" DROP CONSTRAINT IF EXISTS "users_trust_score_range";
ALTER TABLE "users"
  ADD CONSTRAINT "users_trust_score_range"
  CHECK ("trust_score" >= 0.0 AND "trust_score" <= 99.9);