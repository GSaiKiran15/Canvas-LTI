import requests
from django.http import HttpResponse


def index(request):
    canvas_api_url = "https://canvas.instructure.com/api/v1/"
    # Authentication headers (replace with your API token)
    auth_headers = {
        "Authorization": "Bearer 7~tYRfABEynHxxy2cryrQzeLN6DW2BaKzvKcEuB9zmRFXy2nEtBaLYXZAwecVMLcDt"
    }

    # Retrieve course information from the request
    course_id = request.POST.get("custom_course_id")
    course_name = request.POST.get("custom_course_name")

    # Filter only student roles
    enrollment_roles = ["student"]

    # Fetch users enrolled in the course with the role of 'student'
    user_api_response = requests.get(f"{canvas_api_url}courses/{course_id}/users", headers=auth_headers,
                                     params={"enrollment_type[]": enrollment_roles})

    if user_api_response.status_code != 200:
        return HttpResponse(f"API call failed with status code: {user_api_response.status_code}")

    user_data = user_api_response.json()
    students_list = [(student['id'], student['name']) for student in user_data]

    # Fetch assignments for the course
    assignments_api_response = requests.get(f"{canvas_api_url}courses/{course_id}/assignments", headers=auth_headers)

    if assignments_api_response.status_code != 200:
        return HttpResponse(f"Failed to retrieve assignments with status code: {assignments_api_response.status_code}")

    assignment_data = assignments_api_response.json()

    course_summary = []

    # Iterate through students and their assignment submission status
    for student_id, student_name in students_list:
        student_assignments = []

        for assignment in assignment_data:
            assignment_id = assignment['id']
            submission_api_url = f"{canvas_api_url}courses/{course_id}/assignments/{assignment_id}/submissions/{student_id}"
            submission_api_response = requests.get(submission_api_url, headers=auth_headers)

            if submission_api_response.status_code == 200:
                submission_info = submission_api_response.json()
                is_submitted = submission_info.get('workflow_state') == 'submitted'
            else:
                is_submitted = False

            student_assignments.append({
                'Assignment Name': assignment['name'],
                'Submission Status': is_submitted
            })

        course_summary.append({
            'Student Name': student_name,
            'Assignments': student_assignments
        })

    # Prepare the response text
    response_content = f"List of Students and Their Assignment Status for Course {course_name}:\n\n"

    for student in course_summary:
        response_content += f"Student Name: {student['Student Name']}\nAssignments:\n"
        for assignment in student['Assignments']:
            assignment_title = assignment.get('Assignment Name', 'Name not available')
            submission_status = 'Submitted' if assignment.get('Submission Status', False) else 'Not Submitted'
            response_content += f" - Assignment Name: {assignment_title}\n"
            response_content += f"   Submission Status: {submission_status}\n"
        response_content += "\n"

    return HttpResponse(response_content, content_type="text/plain")
