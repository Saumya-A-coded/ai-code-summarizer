/**
 * Manages a list of users in a simple database.
 */
class UserService {
    constructor() {
        this.users = [
            { id: 1, name: 'Alice', email: 'alice@example.com' },
            { id: 2, name: 'Bob', email: 'bob@example.com' }
        ];
    }

    /**
     * Retrieves the full list of users.
     * @returns {Array} A list of user objects.
     */
    getUsers() {
        console.log("Fetching all users...");
        return this.users;
    }

    /**
     * Adds a new user to the list if the email is unique.
     * @param {string} name - The name of the new user.
     * @param {string} email - The unique email of the new user.
     * @returns {Object|null} The new user object or null if the email already exists.
     */
    addUser(name, email) {
        const emailExists = this.users.some(user => user.email === email);
        if (emailExists) {
            console.error("Error: Email already exists.");
            return null;
        }

        const newUser = {
            id: this.users.length + 1,
            name: name,
            email: email
        };

        this.users.push(newUser);
        console.log(`User ${name} added successfully.`);
        return newUser;
    }
}

/**
 * A standalone function to log a message to the console.
 * @param {string} message - The message to be displayed.
 */
function logMessage(message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] - ${message}`);
}