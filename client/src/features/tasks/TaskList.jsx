import TaskItem from "./TaskItem";

export default function TaskList({
  tasks = [],
  onToggle,
  onDelete,
  compact = false,
}) {
  return (
    <div className={compact ? "task-list" : "full-task-list"}>
      {tasks.map((task, index) => (
        <TaskItem
          key={task?.id || task?.task_id || index}
          task={task}
          onToggle={onToggle}
          onDelete={onDelete}
          compact={compact}
        />
      ))}
    </div>
  );
}