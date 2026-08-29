import { apiRequest } from "./apiClient";

export async function getTasks() {
  const data = await apiRequest("/tasks/");

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.tasks)) {
    return data.tasks;
  }

  return [];
}

export async function getTask(taskId) {
  if (!taskId) {
    throw new Error("Task ID is missing.");
  }

  return apiRequest(`/tasks/${taskId}`);
}

export async function updateTask(task) {
  const taskId = task?.id || task?.task_id;

  if (!taskId) {
    throw new Error("Task ID is missing.");
  }

  const currentStatus =
    task?.status ||
    (task?.completed ? "completed" : "open");

  const newStatus =
    currentStatus === "completed"
      ? "open"
      : "completed";

  const payload = {
    description: task?.description || "",
    assigned_to: task?.assigned_to || "",
    deadline: task?.deadline || null,
    status: newStatus,
  };

  const updatedTask = await apiRequest(
    `/tasks/${taskId}`,
    {
      method: "PUT",
      body: JSON.stringify(payload),
    }
  );

  return {
    data: updatedTask,
    status: updatedTask?.status || newStatus,
  };
}

export async function deleteTask(taskId) {
  if (!taskId) {
    throw new Error("Task ID is missing.");
  }

  return apiRequest(`/tasks/${taskId}`, {
    method: "DELETE",
  });
}