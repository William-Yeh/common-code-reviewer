import { useState } from "react";

type Task = { id: string; title: string; priority: number };

export function TaskBoard({ tasks }: { tasks: Task[] }) {
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const sorted = [...tasks].sort((a, b) =>
    order === "asc" ? a.priority - b.priority : b.priority - a.priority,
  );
  return (
    <section>
      <button onClick={() => setOrder(order === "asc" ? "desc" : "asc")}>Reverse</button>
      <ul>
        {sorted.map((task, index) => (
          <li key={index}>
            <input defaultValue={task.title} />
          </li>
        ))}
      </ul>
    </section>
  );
}
