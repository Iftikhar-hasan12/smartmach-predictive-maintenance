# feature/single_eng_report.py

import streamlit as st
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_and_download_report(engine_id, test_df, processor, pred_rul=None, actual_rul=None, health_details=None):
    """Generate and immediately download PDF report"""
    try:
        if not all([pred_rul, actual_rul, health_details]):
            st.error("Missing engine health data. Please analyze the engine first.")
            return

        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()

        # === Title ===
        elements.append(Paragraph(f"Engine {engine_id} - Health Report", styles['Heading1']))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 15))

        # === Summary Table ===
        elements.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_data = [
            ["Metric", "Value"],
            ["Predicted RUL", f"{pred_rul} cycles"],
            ["Actual RUL", f"{actual_rul} cycles"],
            ["Overall Health", f"{health_details['overall_health']}%"],
            ["Status", health_details['health_status']],
            ["RUL Health", f"{health_details['rul_health']}%"],
            ["Sensor Health", f"{health_details['sensor_health']}%"],
            ["Critical Sensors", ", ".join(health_details['critical_sensors']) if health_details['critical_sensors'] else "None"],
            ["Warning Sensors", ", ".join(health_details['warning_sensors']) if health_details['warning_sensors'] else "None"],
        ]

        summary_table = Table(summary_data, colWidths=[2.5*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 15))

        # === Sensor Details ===
        elements.append(Paragraph("Sensor Analysis", styles['Heading2']))
        sensor_data = [["Sensor", "Value", "Status", "Anomaly", "Score (%)"]]

        for sensor_name, info in health_details['sensor_status_today'].items():
            sensor_data.append([
                sensor_name,
                f"{info['value']} {info.get('unit', '')}",
                info['status'].replace('✅', 'OK').replace('⚠️', 'WARN').replace('🚨', 'CRIT'),
                f"{info['anomaly_level']}%",
                f"{info['score']}%",
            ])

        sensor_table = Table(sensor_data, colWidths=[1.7*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        sensor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elements.append(sensor_table)
        elements.append(Spacer(1, 20))

        # === Recommendations ===
        elements.append(Paragraph("Maintenance Recommendations", styles['Heading2']))
        recommendations = generate_recommendations(health_details, pred_rul)
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", styles['Normal']))

        elements.append(Spacer(1, 20))
        # elements.append(Paragraph("End of Report.", styles['Italic']))

        # === Build PDF ===
        doc.build(elements)
        buffer.seek(0)

        # === Download Button ===
        st.download_button(
            label="📥 Click to Download Engine Report (PDF)",
            data=buffer,
            file_name=f"Engine_{engine_id}_Health_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"pdf_download_{engine_id}_{datetime.now().strftime('%H%M%S')}"

            #key=f"pdf_download_{engine_id}"
        )

        st.success("PDF report generated successfully!")

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}")


def generate_recommendations(health_details, pred_rul):
    """Generate maintenance recommendations dynamically"""
    recs = []

    # Based on RUL
    if pred_rul < 20:
        recs.append("Engine nearing failure — immediate maintenance required.")
    elif pred_rul < 50:
        recs.append("Plan maintenance within the next few cycles.")
    else:
        recs.append("Engine is healthy. Continue normal operation.")

    # Based on sensors
    if health_details['critical_sensors']:
        recs.append(f"Critical Sensors: {', '.join(health_details['critical_sensors'])}.")
    if health_details['warning_sensors']:
        recs.append(f"Warning Sensors: {', '.join(health_details['warning_sensors'])}.")
    if not health_details['critical_sensors'] and not health_details['warning_sensors']:
        recs.append("All sensors operating within safe ranges.")

    return recs
