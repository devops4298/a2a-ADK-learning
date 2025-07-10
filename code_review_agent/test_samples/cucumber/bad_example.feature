# This feature file contains intentional Gherkin issues for testing

Feature: Login
  I want to login

@test1 @temp
Scenario: Test login
  When I am on login page
  When I enter credentials
  When I click the submit button with id "login-btn"
  When I should see dashboard

@WIP @TODO
Scenario: User profile update with API call and database validation
  Given the login page is displayed
  And the user database contains valid user records
  When I click the username field
  And I type "testuser" in the input field
  And I click the password field  
  And I type "password123" in the password input
  And I click the login button element
  And I wait for the API response to return status 200
  And the database is updated with login timestamp
  Then I should see the dashboard page loaded
  And the user session should be stored in the database
  And the login API should return the correct JSON response

Scenario: 
  Given I am logged in
  Then I can see my profile

Background:
  Given I have a browser open
  And I navigate to the application URL
  And I wait for the page to load completely
  And I accept all cookies
  And I dismiss any popup notifications
  And I verify the page title contains "Application"

Scenario: Another test
  # This scenario depends on the previous one
  When I go to settings
  Then I can change my password
