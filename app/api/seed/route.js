import { seedTransactions } from "@/actions/seed";

export async function GET() {
  const result = await seedTransactions();
  return Response.json(result);
}
# updated 2024-10-01 10:11:27
