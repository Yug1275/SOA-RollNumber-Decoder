SCREENSHOTS FOLDER — READ ME
============================

This folder is for Postman screenshots that you capture manually.

REQUIRED SCREENSHOT (for assignment submission)
-----------------------------------------------
1. Open Postman.
2. Import postman_collection.json (File → Import → Upload Files).
3. Make sure the Flask server is running:
      cd Student-Roll-Number-Decoder
      venv\Scripts\activate
      python app.py
4. In Postman, open "Test 1 – Computer Engineering, 2023 batch (23BCP242)".
5. Click Send.
6. Verify the response shows HTTP 200 and the correct JSON body.
7. Take a screenshot of the entire Postman window showing:
      - The request (POST, URL, JSON body on the left side)
      - The response body on the right/bottom side
8. Save the screenshot as:
      screenshots\postman_test1_23BCP242.png

OPTIONAL ADDITIONAL SCREENSHOTS
--------------------------------
You may capture screenshots for each of the 13 test cases.
Suggested file names:
    postman_test2_23BIT187.png
    postman_test3_24BCP045.png
    postman_test4_25BIT003.png
    postman_test5_26BCP036.png
    postman_test6_24BCP424D_suffix.png
    postman_test7_missing_field.png
    postman_test8_empty.png
    postman_test9_invalid_format.png
    postman_test10_unknown_branch.png
    postman_test11_malformed_json.png
    postman_test12_wrong_method.png
    postman_test13_health_check.png

NOTE
----
Do NOT add the virtual environment folder (venv/) to the screenshots folder
or to the ZIP file you submit on Microsoft Teams.
