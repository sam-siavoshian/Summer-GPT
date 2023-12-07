// $(document).ready(function () {
//     // Load saved user and AI messages from local storage
//     var savedUserMessages = JSON.parse(localStorage.getItem('userMessages')) || [];
//     var savedAIMessages = JSON.parse(localStorage.getItem('aiMessages')) || [];

//     // Function to save a message to local storage
//     function saveUserMessage(message) {
//         savedUserMessages.push(message);
//         localStorage.setItem('userMessages', JSON.stringify(savedUserMessages));
//     }

//     function saveAIMessage(message) {
//         savedAIMessages.push(message);
//         localStorage.setItem('aiMessages', JSON.stringify(savedAIMessages));
//     }

//     // Function to display saved messages
//     function displaySavedMessages() {
//         savedUserMessages.forEach(function (message) {
//             if (message) { // Check if the message is not empty
//                 var messageDiv = $('<div class="message user"></div>');
//                 messageDiv.text(message);
//                 $('.chatbox').append(messageDiv);
//             }
//         });

//         savedAIMessages.forEach(function (message) {
//             if (message) { // Check if the message is not empty
//                 var messageDiv = $('<div class="message ai"></div>');
//                 messageDiv.text(message);
//                 $('.chatbox').append(messageDiv);
//             }
//         });
//     }

//     // Display saved messages when the page loads
//     displaySavedMessages();
    
//     var isNotificationVisible = false; // Variable to track notification visibility

//     $('#chatForm').submit(function (e) {
//         e.preventDefault();
//         var userInput = $('#userMessage').val();

//         // Check if the input is empty
//         if (userInput.trim() === '') {
//             // Show the notification only if it's not already visible
//             if (!isNotificationVisible) {
//                 showNotification();

//                 // Hide the notification after 5 seconds (adjust the duration as needed)
//                 setTimeout(hideNotification, 5000);
//             }

//             return; // Do not proceed further
//         }

//         // Save the user message to local storage
//         saveUserMessage(userInput);

//         $.ajax({
//             type: 'POST',
//             url: '/send_message',
//             data: { userInput: userInput },
//             success: function (data) {
//                 console.log(data); // Log the response to the console

//                 // Create a new AI message div with the "message ai" class
//                 var aiMessageDiv = $('<div class="message ai"></div>');
//                 aiMessageDiv.text(data.response);

//                 // Append the AI message to the chatbox
//                 $('.chatbox').append(aiMessageDiv);

//                 // Save the AI response to local storage
//                 saveAIMessage(data.response);

//                 // Scroll to the bottom of the chatbox to show the latest message
//                 var chatbox = $('.chatbox');
//                 chatbox.scrollTop(chatbox[0].scrollHeight);

//                 // Clear the input field
//                 $('#userMessage').val('');
//             },
//             error: function (error) {
//                 console.error(error); // Log any errors to the console
//             }
//         });
//     });

//     function showNotification() {
//         var notification = document.getElementById('notification');
//         var timer = document.getElementById('notification-timer');
//         notification.style.display = 'block';

//         // Animate the line width from 100% to 0% over 5 seconds (adjust duration as needed)
//         $(timer).animate({ width: '0%' }, 5000, function () {
//             hideNotification();
//         });

//         isNotificationVisible = true; // Set notification visibility to true
//     }

//     function hideNotification() {
//         var notification = document.getElementById('notification');
//         notification.style.display = 'none';

//         isNotificationVisible = false; // Set notification visibility to false
//     }
// });