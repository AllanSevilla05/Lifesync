import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import './TaskManager.css';

const TaskManager = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newTask, setNewTask] = useState({
        title: '',
        description: '',
        priority: 1,
        due_date: '',
    });

    useEffect(() => {
        loadTasks();
    }, []);

    const loadTasks = async () => {
        try {
            const tasksData = await apiService.getTasks();
            setTasks(tasksData);
        } catch (error) {
            console.error('Failed to load tasks:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateTask = async (e) => {
        e.preventDefault();
        try {
            const createdTask = await apiService.createTask(newTask);
            setTasks([...tasks, createdTask]);
            setNewTask({ title: '', description: '', priority: 1, due_date: '' });
        } catch (error) {
            console.error('Failed to create task:', error);
        }
    };

    const handleUpdateTask = async (taskId, updates) => {
        try {
            const updatedTask = await apiService.updateTask(taskId, updates);
            setTasks(tasks.map(task => 
                task.id === taskId ? updatedTask : task
            ));
        } catch (error) {
            console.error('Failed to update task:', error);
        }
    };

    const handleDeleteTask = async (taskId) => {
        try {
            await apiService.deleteTask(taskId);
            setTasks(tasks.filter(task => task.id !== taskId));
        } catch (error) {
            console.error('Failed to delete task:', error);
        }
    };

    if (loading) {
        return <div>Loading tasks...</div>;
    }

    return (
        <div className="task-manager">
            <h2>Task Manager</h2>
            
            {/* Create Task Form */}
            <form onSubmit={handleCreateTask} className="task-form">
                <input
                    type="text"
                    placeholder="Task title"
                    value={newTask.title}
                    onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                    required
                />
                <textarea
                    placeholder="Task description"
                    value={newTask.description}
                    onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                />
                <select
                    value={newTask.priority}
                    onChange={(e) => setNewTask({...newTask, priority: parseInt(e.target.value)})}
                >
                    <option value={1}>Low Priority</option>
                    <option value={2}>Medium Priority</option>
                    <option value={3}>High Priority</option>
                </select>
                <input
                    type="datetime-local"
                    value={newTask.due_date}
                    onChange={(e) => setNewTask({...newTask, due_date: e.target.value})}
                />
                <button type="submit">Create Task</button>
            </form>

            {/* Task List */}
            <div className="task-list">
                {tasks.map(task => (
                    <div key={task.id} className="task-item">
                        <h3>{task.title}</h3>
                        <p>{task.description}</p>
                        <div className="task-meta">
                            <span>Priority: {task.priority}</span>
                            <span>Status: {task.status}</span>
                            {task.due_date && (
                                <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
                            )}
                        </div>
                        <div className="task-actions">
                            <button
                                onClick={() => handleUpdateTask(task.id, { status: 'completed' })}
                                disabled={task.status === 'completed'}
                            >
                                Mark Complete
                            </button>
                            <button
                                onClick={() => handleDeleteTask(task.id)}
                                className="delete-btn"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TaskManager; 