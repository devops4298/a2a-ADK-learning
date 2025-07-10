// This file contains intentional code quality issues for testing

let user_name = "john";  // Should use camelCase
const max_retries = 3;   // Should use UPPER_SNAKE_CASE for constants

class userService {      // Should use PascalCase
    
    // Function without explicit types
    processUser(user) {
        console.log("Processing user:", user);  // Should remove console.log
        return user.name;  // No null checking
    }
    
    // Function that's too long and does multiple things
    validateAndSaveUser(userData) {
        // Validation
        if (!userData) {
            throw new Error("No data");
        }
        if (!userData.email) {
            throw new Error("No email");
        }
        if (!userData.name) {
            throw new Error("No name");
        }
        if (userData.age < 18) {
            throw new Error("Too young");
        }
        
        // Transformation
        userData.email = userData.email.toLowerCase();
        userData.name = userData.name.trim();
        
        // Saving
        const db = this.getDatabase();
        const result = db.save(userData);
        
        // Logging
        console.log("User saved:", result);
        
        // Notification
        this.sendWelcomeEmail(userData.email);
        
        return result;
    }
    
    // Using 'any' type
    handleApiResponse(response: any) {
        return response.data;
    }
    
    // Unused import would be here
    // import { unusedFunction } from './utils';
}

// Missing semicolon
let config = { timeout: 5000 }

// Double quotes instead of single quotes
const message = "Hello world";

// No error handling for async function
async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
}
