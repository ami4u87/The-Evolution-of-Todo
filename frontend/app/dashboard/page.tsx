"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import TaskForm from "@/components/tasks/TaskForm";
import TaskList from "@/components/tasks/TaskList";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  markTaskComplete,
  ApiClientError,
} from "@/lib/api-client";
import type { Task, TaskCreate, TaskUpdate } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load tasks on mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setError(null);
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      console.error("Failed to load tasks:", err);

      if (err instanceof ApiClientError && err.statusCode === 401) {
        // Unauthorized - redirect to login
        router.push("/login");
        return;
      }

      setError("Failed to load tasks. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (data: TaskCreate) => {
    try {
      const newTask = await createTask(data);
      setTasks((prev) => [newTask, ...prev]);
    } catch (err) {
      console.error("Failed to create task:", err);
      throw err; // Re-throw so TaskForm can handle it
    }
  };

  const handleUpdateTask = async (
    taskId: string,
    updates: Partial<Task>
  ) => {
    try {
      const taskUpdate: TaskUpdate = {
        title: updates.title,
        description: updates.description,
        status: updates.status,
      };

      const updatedTask = await updateTask(taskId, taskUpdate);

      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
    } catch (err) {
      console.error("Failed to update task:", err);
      throw err;
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err) {
      console.error("Failed to delete task:", err);
      throw err;
    }
  };

  const handleToggleComplete = async (taskId: string) => {
    try {
      const task = tasks.find((t) => t.id === taskId);
      if (!task) return;

      if (task.status === "completed") {
        // Uncomplete: update status to pending
        await handleUpdateTask(taskId, { status: "pending" });
      } else {
        // Mark complete
        const updatedTask = await markTaskComplete(taskId);
        setTasks((prev) =>
          prev.map((t) => (t.id === taskId ? updatedTask : t))
        );
      }
    } catch (err) {
      console.error("Failed to toggle task:", err);
      throw err;
    }
  };

  const handleLogout = () => {
    // Clear auth token (will be replaced with Better Auth)
    localStorage.removeItem("auth_token");
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              My Tasks
            </h1>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-medium">Error</p>
            <p className="text-sm mt-1">{error}</p>
            <button
              onClick={loadTasks}
              className="mt-2 text-sm underline hover:no-underline"
            >
              Retry
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Task Form - Left Column */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <TaskForm onSubmit={handleCreateTask} />
            </div>
          </div>

          {/* Task List - Right Column */}
          <div className="lg:col-span-2">
            <TaskList
              tasks={tasks}
              onUpdate={handleUpdateTask}
              onDelete={handleDeleteTask}
              onToggleComplete={handleToggleComplete}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
