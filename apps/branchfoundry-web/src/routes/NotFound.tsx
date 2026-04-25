import { Link } from "react-router-dom";
import { Button, Empty } from "@foundry/ui";

export default function NotFound() {
  return (
    <Empty
      title="Page not found"
      description="That route doesn't exist. Try returning to the dashboard."
      action={
        <Link to="/">
          <Button variant="secondary">Back to dashboard</Button>
        </Link>
      }
    />
  );
}
