"""
Generate workout Excel file with exercises, weights from history, and checkboxes for each set
"""
import psycopg
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
import json
from datetime import date
from src.utils import connect_to_database
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, DB_HOST

def get_last_weight_used(cur, exercise_id, reps):
    """
    Get the last weight used for an exercise with given reps
    Returns the most recent weight from workout history
    """
    cur.execute("""
        SELECT se.weight_used, ws.session_date
        FROM session_exercises se
        JOIN workout_sessions ws ON se.session_id = ws.session_id
        WHERE se.exercise_id = %s 
          AND se.reps_completed = %s
        ORDER BY ws.session_date DESC, se.set_number DESC
        LIMIT 1
    """, (exercise_id, reps))
    
    result = cur.fetchone()
    return result[0] if result else None


def generate_workout_excel(plan_name, day_of_week, output_file="workout.xlsx"):
    """
    Generate Excel workout tracker for a specific day
    
    Args:
        plan_name: Name of the training plan (e.g., "Plan Luty 2025")
        day_of_week: Day to generate (e.g., "Monday", "Wednesday", "Friday")
        output_file: Output Excel filename
    """
    
    # Connect to database
    conn, cur = connect_to_database()
    
    try:
        # Get plan_id
        cur.execute("""
            SELECT plan_id FROM training_plans WHERE plan_name = %s
        """, (plan_name,))
        
        result = cur.fetchone()
        if not result:
            log(f"Plan '{plan_name}' not found!", level="ERROR", echo=True)
            return
        
        plan_id = result[0]
        
        # Get exercises for this day
        cur.execute("""
            SELECT 
                e.exercise_id,
                e.exercise_name,
                pe.warmup_sets,
                pe.working_sets,
                pe.reps,
                pe.planned_weight,
                pe.rest_between_sets_min,
                pe.rest_between_sets_max,
                pe.rest_after_exercise_min,
                pe.rest_after_exercise_max
            FROM plan_exercises pe
            JOIN exercises e ON pe.exercise_id = e.exercise_id
            WHERE pe.plan_id = %s AND pe.day_of_week = %s
            ORDER BY pe.plan_exercise_id
        """, (plan_id, day_of_week))
        
        exercises = cur.fetchall()
        
        if not exercises:
            log(f"No exercises found for {day_of_week} in '{plan_name}'", level="ERROR", echo=True)
            return
        
        # Create workbook
        wb = Workbook()
        sheet = wb.active
        sheet.title = f"{day_of_week}"
        checkbox_dv = DataValidation(type="list", formula1='"☐,☑"', allow_blank=True)
        sheet.add_data_validation(checkbox_dv)
        
        # Define styles
        header_font = Font(bold=True, size=11)
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font_white = Font(bold=True, size=11, color="FFFFFF")
        center_align = Alignment(horizontal="center", vertical="center")
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Set column widths
        sheet.column_dimensions['A'].width = 25  # Exercise name
        sheet.column_dimensions['B'].width = 12  # Weight
        sheet.column_dimensions['C'].width = 12  # Warmup sets
        sheet.column_dimensions['D'].width = 12  # Working sets
        sheet.column_dimensions['E'].width = 12  # Reps
        sheet.column_dimensions['F'].width = 12  # Rest between sets
        sheet.column_dimensions['G'].width = 12  # Rest after
        sheet.column_dimensions['H'].width = 10  # Comment
        
        # Add checkboxes columns (one per set)
        max_total_sets = max(
            (ex[2] or 0) + ex[3] for ex in exercises
        )
        for i in range(max_total_sets):
            col_letter = chr(73 + i)  # Start from column I
            sheet.column_dimensions[col_letter].width = 4
        
        # Header row
        headers = [
            "Ćwiczenie", "Ciężar", "Serie rozgrzewkowe", 
            "Serie właściwe", "Powtórzenia", "Przerwa", 
            "Przerwa po", "Comment"
        ]
        
        for col_idx, header in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_idx)
            cell.value = header
            cell.font = header_font_white
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border
        
        # Add checkbox headers
        for i in range(max_total_sets):
            cell = sheet.cell(row=1, column=9 + i)
            cell.value = "✓"
            cell.font = header_font_white
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border
        
        # Add exercises
        current_row = 2
        
        for exercise in exercises:
            (exercise_id, exercise_name, warmup_sets, working_sets, 
             reps_json, planned_weight, rest_min, rest_max, 
             rest_after_min, rest_after_max) = exercise
            
            try:
                reps_list = json.loads(reps_json) if reps_json else []
            except (json.JSONDecodeError, TypeError):
                reps_list = []
            
            # Get weight suggestion from history (use first rep count)
            suggested_weight = None
            if reps_list and isinstance(reps_list[0], int):
                suggested_weight = get_last_weight_used(cur, exercise_id, reps_list[0])
            
            # Use suggested weight if available, otherwise use planned_weight
            weight_display = suggested_weight if suggested_weight is not None else (planned_weight if planned_weight else "")
            
            # Format rest times
            rest_between = f"{rest_min}-{rest_max}" if rest_min and rest_max and rest_min != rest_max else str(rest_min) if rest_min else ""
            rest_after = f"{rest_after_min}-{rest_after_max}" if rest_after_min and rest_after_max and rest_after_min != rest_after_max else str(rest_after_min) if rest_after_min else ""
            
            # Add exercise row
            sheet.cell(row=current_row, column=1).value = exercise_name
            sheet.cell(row=current_row, column=2).value = weight_display
            sheet.cell(row=current_row, column=3).value = warmup_sets or 0
            sheet.cell(row=current_row, column=4).value = working_sets
            sheet.cell(row=current_row, column=5).value = ", ".join(str(r) for r in reps_list) if reps_list else ""
            sheet.cell(row=current_row, column=6).value = rest_between
            sheet.cell(row=current_row, column=7).value = rest_after
            
            # Add borders
            for col in range(1, 9):
                sheet.cell(row=current_row, column=col).border = thin_border
                sheet.cell(row=current_row, column=col).alignment = Alignment(vertical="center")
            
            # Center align numeric columns
            for col in [2, 3, 4, 6, 7]:
                sheet.cell(row=current_row, column=col).alignment = center_align
            
            # Add checkboxes for each set (warmup + working)
            total_sets = (warmup_sets or 0) + working_sets
            for set_num in range(total_sets):
                checkbox_col = 9 + set_num
                cell = sheet.cell(row=current_row, column=checkbox_col)
                cell.value = "☐"  # Empty checkbox
                cell.alignment = center_align
                cell.border = thin_border
                cell.font = Font(size=14)
                checkbox_dv.add(cell)
            
            current_row += 1
        
        # Save workbook
        wb.save(str(output_file))
        print(f"Workout Excel generated: {output_file}")
        print(f"Plan: {plan_name}")
        print(f"Day: {day_of_week}")
        print(f"Exercises: {len(exercises)}")
        
    finally:
        cur.close()
        conn.close()
