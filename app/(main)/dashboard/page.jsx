import { getDashboardSummary } from "@/actions/dashboard";
import { AccountCard } from "./_components/account-card";
import { CreateAccountDrawer } from "@/components/create-account-drawer";
import { BudgetProgress } from "./_components/budget-progress";
import { Card, CardContent } from "@/components/ui/card";
import { Plus } from "lucide-react";
import { DashboardOverview } from "./_components/transaction-overview";

export default async function DashboardPage() {
  const { accounts, transactions, budgetData } = await getDashboardSummary();

  return (
    <div className="space-y-8">
      {/* Budget Progress */}
      <BudgetProgress
        initialBudget={budgetData?.budget}
        currentExpenses={budgetData?.currentExpenses || 0}
      />

      {/* Dashboard Overview */}
      <DashboardOverview
        accounts={accounts}
        transactions={transactions || []}
      />

      {/* Accounts Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <CreateAccountDrawer>
          <Card className="hover:shadow-md transition-shadow cursor-pointer border-dashed">
            <CardContent className="flex flex-col items-center justify-center text-muted-foreground h-full pt-5">
              <Plus className="h-10 w-10 mb-2" />
              <p className="text-sm font-medium">Add New Account</p>
            </CardContent>
          </Card>
        </CreateAccountDrawer>
        {accounts.length > 0 &&
          accounts?.map((account) => (
            <AccountCard key={account.id} account={account} />
          ))}
      </div>
    </div>
  );
}
# updated 2024-02-05 11:17:42
# updated 2024-02-08 10:33:27
# updated 2024-02-05 11:17:42
# updated 2024-02-08 10:33:27
# updated 2024-05-09 14:22:09
# updated 2024-10-14 09:52:16
# updated 2025-04-02 10:48:16
# updated 2025-04-28 10:29:38
# updated 2025-06-10 11:20:00
# updated 2025-06-12 16:15:00
# updated 2025-06-18 11:10:00
# updated 2025-06-21 09:10:00
# updated 2025-06-24 13:00:00
# updated 2025-07-03 09:00:00
