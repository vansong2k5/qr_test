import { Card, CardContent, CardHeader, CardTitle } from "../components/Card";

export const Dashboard = () => {
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total QR Codes</CardTitle>
          </CardHeader>
          <CardContent>128</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Scans (7d)</CardTitle>
          </CardHeader>
          <CardContent>542</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Top Product</CardTitle>
          </CardHeader>
          <CardContent>Widget Pro</CardContent>
        </Card>
      </div>
    </div>
  );
};
