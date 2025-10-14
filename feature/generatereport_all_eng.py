import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io
import streamlit as st
from datetime import datetime

def analyze_sensor_issues(engine_health_scores, engine_details, processor, test_df):
    """Analyze which sensors are most frequently causing issues across the fleet"""
    
    # Initialize counters
    critical_sensor_counts = {sensor_name: 0 for sensor_name in processor.sensor_mapping.values()}
    warning_sensor_counts = {sensor_name: 0 for sensor_name in processor.sensor_mapping.values()}
    
    # Count sensor issues across all engines
    for engine_id in engine_health_scores.keys():
        # Get the latest sensor readings for this engine
        engine_data = test_df[test_df['unit_number'] == engine_id].tail(1)
        
        if not engine_data.empty:
            # Check each sensor against its thresholds
            for sensor_col, sensor_name in processor.sensor_mapping.items():
                if sensor_col in engine_data.columns:
                    value = engine_data[sensor_col].iloc[0]
                    low, high = processor.sensor_thresholds.get(sensor_col, (0, 1))
                    
                    # Check if sensor is out of range
                    if value < low:
                        warning_sensor_counts[sensor_name] += 1
                    elif value > high:
                        critical_sensor_counts[sensor_name] += 1
    
    return critical_sensor_counts, warning_sensor_counts

def create_sensor_bar_chart(sensor_counts, title, color):
    """Create a bar chart for sensor issue frequency"""
    
    # Filter out sensors with zero counts and sort by count
    filtered_counts = {k: v for k, v in sensor_counts.items() if v > 0}
    if not filtered_counts:
        return None
    
    # Sort by count (descending)
    sorted_items = sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True)
    sensors = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(sensors, counts, color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # Customize the chart
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Sensors', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Engines Affected', fontsize=12, fontweight='bold')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=10)
    
    # Add value labels on bars
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{count}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    buffer.seek(0)
    
    return buffer

def generate_fleet_report(engine_health_scores, engine_details, test_df, processor):
    """Generate professional PDF fleet health report with charts"""
    
    try:
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Center aligned
            textColor=colors.HexColor('#2E86AB')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#2E86AB')
        )
        
        # Header
        elements.append(Paragraph("INDUSTRIAL FLEET HEALTH REPORT", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # 1. Executive Summary
        elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
        
        # Calculate statistics
        total_engines = len(engine_health_scores)
        critical_engines = {eid: score for eid, score in engine_health_scores.items() if score < 41}
        warning_engines = {eid: score for eid, score in engine_health_scores.items() if 41 <= score < 65}
        good_engines = {eid: score for eid, score in engine_health_scores.items() if score >= 65}
        
        summary_data = [
            ['Metric', 'Count', 'Percentage'],
            ['Total Engines', str(total_engines), '100%'],
            ['Good Condition', str(len(good_engines)), f"{len(good_engines)/total_engines*100:.1f}%"],
            ['Requires Monitoring', str(len(warning_engines)), f"{len(warning_engines)/total_engines*100:.1f}%"],
            ['Critical Attention', str(len(critical_engines)), f"{len(critical_engines)/total_engines*100:.1f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # 2. Health Distribution Chart
        elements.append(Paragraph("FLEET HEALTH DISTRIBUTION", heading_style))
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        sizes = [len(good_engines), len(warning_engines), len(critical_engines)]
        labels = [f'Good\n({sizes[0]} engines)', f'Warning\n({sizes[1]} engines)', f'Critical\n({sizes[2]} engines)']
        colors_pie = ['#28a745', '#ffc107', '#dc3545']
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                         startangle=90, textprops={'fontsize': 10})
        
        # Improve autotext appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Fleet Health Distribution', fontsize=12, fontweight='bold')
        
        # Save chart to buffer
        chart_buffer = io.BytesIO()
        plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        
        chart_buffer.seek(0)
        chart_image = Image(chart_buffer, width=5*inch, height=3.5*inch)
        elements.append(chart_image)
        elements.append(Spacer(1, 20))
        
        # 3. SENSOR ISSUE ANALYSIS - NEW SECTION
        elements.append(Paragraph("SENSOR ISSUE ANALYSIS", heading_style))
        elements.append(Paragraph("Identifying Most Problematic Sensors Across Fleet", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Analyze sensor issues using actual sensor data
        critical_sensor_counts, warning_sensor_counts = analyze_sensor_issues(
            engine_health_scores, engine_details, processor, test_df
        )
        
        # Create Critical Sensors Bar Chart
        critical_chart_buffer = create_sensor_bar_chart(
            critical_sensor_counts, 
            "Most Frequently Critical Sensors", 
            '#dc3545'  # Red color for critical
        )
        
        if critical_chart_buffer:
            critical_chart_image = Image(critical_chart_buffer, width=6*inch, height=4*inch)
            elements.append(Paragraph("Critical Sensors Frequency", styles['Heading3']))
            elements.append(critical_chart_image)
            elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph("No critical sensor issues detected across the fleet.", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Create Warning Sensors Bar Chart
        warning_chart_buffer = create_sensor_bar_chart(
            warning_sensor_counts, 
            "Most Frequently Warning Sensors", 
            '#ffc107'  # Yellow color for warning
        )
        
        if warning_chart_buffer:
            warning_chart_image = Image(warning_chart_buffer, width=6*inch, height=4*inch)
            elements.append(Paragraph("Warning Sensors Frequency", styles['Heading3']))
            elements.append(warning_chart_image)
        else:
            elements.append(Paragraph("No warning sensor issues detected across the fleet.", styles['Normal']))
        
        elements.append(Spacer(1, 20))
        
        # 4. Critical Engines Details
        if critical_engines:
            elements.append(Paragraph("🚨 CRITICAL ENGINES - IMMEDIATE ATTENTION REQUIRED", heading_style))
            
            critical_data = [['Engine ID', 'Health %', 'Pred RUL', 'Actual RUL', 'Critical Sensors']]
            for eid, score in sorted(critical_engines.items()):
                details = engine_details[eid]
                critical_data.append([
                    str(eid),
                    f"{score:.1f}%",
                    str(details['pred_rul']),
                    str(details['actual_rul']),
                    str(details['critical_sensors'])
                ])
            
            critical_table = Table(critical_data, colWidths=[0.8*inch, 1*inch, 0.8*inch, 0.8*inch, 1.2*inch])
            critical_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFE5E5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            
            elements.append(critical_table)
            elements.append(Spacer(1, 15))
        
        # 5. Complete Engine Health Data
        elements.append(Paragraph("COMPLETE ENGINE HEALTH DATA", heading_style))
        
        # Prepare table data
        table_data = [['Engine ID', 'Health %', 'Status', 'Pred RUL', 'Act RUL', 'Crit Sens', 'Warn Sens']]
        
        for eid, score in sorted(engine_health_scores.items()):
            details = engine_details[eid]
            
            # Determine status color coding
            status_text = details['health_status'].replace('✅', '').replace('⚠️', '').replace('🚨', '').strip()
            
            table_data.append([
                str(eid),
                f"{score:.1f}%",
                status_text,
                str(details['pred_rul']),
                str(details['actual_rul']),
                str(details['critical_sensors']),
                str(details['warning_sensors'])
            ])
        
        # Create main table
        main_table = Table(table_data, colWidths=[0.7*inch, 0.8*inch, 1*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.7*inch])
        
        # Table styling
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        
        # Add row coloring based on status
        for i in range(1, len(table_data)):
            score = engine_health_scores[int(table_data[i][0])]
            if score < 41:
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFE5E5'))
            elif score < 65:
                style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#FFF3CD'))
        
        main_table.setStyle(style)
        elements.append(main_table)
        
        # 6. Footer
        elements.append(Spacer(1, 20))
        #elements.append(Paragraph("*** End of Report ***", styles['Normal']))
        elements.append(Paragraph("Generated by SmartMach System", 
                                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=1)))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return None

def create_csv_report(engine_health_scores, engine_details):
    """Generate CSV report as alternative format"""
    try:
        # Prepare data for CSV
        data = []
        for eid, score in sorted(engine_health_scores.items()):
            details = engine_details[eid]
            
            # Determine status
            if score >= 65:
                status = "GOOD"
            elif score >= 41:
                status = "WARNING"
            else:
                status = "CRITICAL"
            
            data.append({
                'Engine_ID': eid,
                'Health_Score_Percent': score,
                'Status': status,
                'Predicted_RUL': details['pred_rul'],
                'Actual_RUL': details['actual_rul'],
                'Critical_Sensors': details['critical_sensors'],
                'Warning_Sensors': details['warning_sensors']
            })
        
        # Create DataFrame and CSV
        df = pd.DataFrame(data)
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return csv_buffer
        
    except Exception as e:
        st.error(f"Error generating CSV: {str(e)}")
        return None