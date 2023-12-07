document.addEventListener('DOMContentLoaded', function () {
    const chatbox = document.querySelector('.chatbox');
    const sendMessageBtn = document.querySelector('.sendMessage');
    const userMessageInput = document.getElementById('userMessage');

    // Load saved messages from local storage on page load
    const savedMessages = JSON.parse(localStorage.getItem('chatMessages')) || [];
    savedMessages.forEach((messageData) => {
        displayMessage(messageData.text, messageData.sender);
    });

    sendMessageBtn.addEventListener('click', () => {
        const messageText = userMessageInput.value.trim();


        if (messageText !== '') {
            // Create a chat bubble for the user's typed message
            displayMessage(messageText, 'user');

            // Save the message to local storage
            saveMessage(messageText, 'user');

            // Clear the input field
            userMessageInput.value = '';
        }
    });

    // Add right-click (contextmenu) event listener to chatbox
    chatbox.addEventListener('contextmenu', (e) => {
        e.preventDefault();

        if (e.target.classList.contains('message') && e.target.classList.contains('user')) {
            // Show the delete icon
            const deleteIcon = document.querySelector('.delete-icon');
            deleteIcon.style.display = 'block';

            // Set the position of the delete icon
            const rect = e.target.getBoundingClientRect();
            deleteIcon.style.top = `${rect.top + window.scrollY}px`;
            deleteIcon.style.left = `${rect.right + window.scrollX}px`;

            // Set a custom attribute to remember the message element
            deleteIcon.setAttribute('data-message', e.target.textContent);
        }
    });

    // Add click event listener to delete icon
    const deleteIcon = document.querySelector('.delete-icon');
    deleteIcon.addEventListener('click', () => {
        // Retrieve the message text from the custom attribute
        const messageText = deleteIcon.getAttribute('data-message');

        // Find and remove the message from the chatbox
        const messages = chatbox.querySelectorAll('.message.user');
        messages.forEach((message) => {
            if (message.textContent === messageText) {
                message.remove();

                // Remove the message from local storage
                removeMessageFromStorage(messageText);
            }
        });

        // Hide the delete icon
        deleteIcon.style.display = 'none';
    });

    // Handle closing the delete icon if clicked elsewhere
    document.addEventListener('click', (e) => {
        if (!e.target.classList.contains('delete-icon')) {
            deleteIcon.style.display = 'none';
        }
    });

    function displayMessage(text, sender) {
        // Create a chat bubble for the message
        const message = document.createElement('div');
        message.className = `message ${sender}`;
        message.textContent = text;

        // Style the AI's messages with a pink background on the right
        if (sender === 'ai') {
            message.classList.add('ai'); // Add the 'ai' class for styling
        }

        // Create a delete icon for the message
        const deleteIcon = document.createElement('div');
        deleteIcon.className = 'delete-icon';
        deleteIcon.innerHTML = '<i class="fas fa-trash-alt"></i>';

        // Add the message and delete icon to the chatbox
        const messageContainer = document.createElement('div');
        messageContainer.appendChild(message);
        messageContainer.appendChild(deleteIcon);
        chatbox.appendChild(messageContainer);

        // Scroll to the bottom of the chatbox
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function saveMessage(text, sender) {
        // Load existing messages from local storage
        const existingMessages = JSON.parse(localStorage.getItem('chatMessages')) || [];

        // Add the new message to the existing messages
        existingMessages.push({ text, sender });

        // Save the updated messages back to local storage
        localStorage.setItem('chatMessages', JSON.stringify(existingMessages));
    }

    function removeMessageFromStorage(messageText) {
        // Load existing messages from local storage
        const existingMessages = JSON.parse(localStorage.getItem('chatMessages')) || [];

        // Remove the message with matching text
        const updatedMessages = existingMessages.filter((message) => message.text !== messageText);

        // Save the updated messages back to local storage
        localStorage.setItem('chatMessages', JSON.stringify(updatedMessages));
    }

    // Listen for Enter key press in the input field
    userMessageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent the default Enter key behavior (new line)
            sendMessage(); // Call the sendMessage function to send the message
        }
    });

    // Function to send the message
    function sendMessage(userMessage, aiResponse) {
        if (userMessage !== '') {
            // Create a chat bubble for the user's typed message
            displayMessage(userMessage, 'user');

            // Create a chat bubble for the AI's response
            displayMessage(aiResponse, 'ai');

            // Save the user's message to local storage
            saveMessage(userMessage, 'user');

            // Save the AI's response to local storage
            saveMessage(aiResponse, 'ai');

            // Clear the input field
            userMessageInput.value = '';
        }
    }
});