#!/usr/bin/env python3
"""
Web dashboard for job tracker - view jobs, manage applications, monitor health.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from src.core.database import get_db_context
from src.core.models import Job, Alert
from src.ingest.health_monitor import HealthMonitor, URLHealth

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
    """Dashboard home page."""
    with get_db_context() as db:
        # Get statistics
        total_jobs = db.query(Job).filter(Job.is_active == True).count()
        new_jobs_today = db.query(Job).filter(
            Job.first_seen_at >= datetime.now() - timedelta(days=1)
        ).count()
        
        companies = db.query(Job.company).distinct().count()
        
        # Get recent jobs
        recent_jobs = db.query(Job).filter(
            Job.is_active == True
        ).order_by(desc(Job.first_seen_at)).limit(10).all()
        
        # Get jobs by category
        jobs_by_category = db.query(
            Job.category, func.count(Job.id)
        ).filter(Job.is_active == True).group_by(Job.category).all()
        
        return render_template(
            'dashboard.html',
            total_jobs=total_jobs,
            new_jobs_today=new_jobs_today,
            companies=companies,
            recent_jobs=recent_jobs,
            jobs_by_category=jobs_by_category
        )


@app.route('/jobs')
def jobs():
    """List all jobs with filters."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    company_filter = request.args.get('company', '')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', 'active')
    
    with get_db_context() as db:
        query = db.query(Job)
        
        # Apply filters
        if status_filter == 'active':
            query = query.filter(Job.is_active == True)
        
        if company_filter:
            query = query.filter(Job.company.ilike(f'%{company_filter}%'))
        
        if category_filter:
            query = query.filter(Job.category == category_filter)
        
        # Get total count
        total = query.count()
        
        # Paginate
        jobs = query.order_by(desc(Job.first_seen_at)).offset(
            (page - 1) * per_page
        ).limit(per_page).all()
        
        # Get all categories for filter
        categories = db.query(Job.category).distinct().filter(
            Job.category.isnot(None)
        ).all()
        categories = [c[0] for c in categories]
        
        return render_template(
            'jobs.html',
            jobs=jobs,
            page=page,
            per_page=per_page,
            total=total,
            categories=categories,
            company_filter=company_filter,
            category_filter=category_filter
        )


@app.route('/job/<job_id>')
def job_detail(job_id):
    """Job details page."""
    with get_db_context() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return "Job not found", 404
        
        return render_template('job_detail.html', job=job)


@app.route('/health')
def health():
    """System health monitoring."""
    health_monitor = HealthMonitor()
    
    with get_db_context() as db:
        summary = health_monitor.get_health_summary()
        failing_urls = health_monitor.get_failing_urls(min_failures=3)
        
        # Get all health records
        all_health = db.query(URLHealth).order_by(desc(URLHealth.failure_count)).all()
        
        return render_template(
            'health.html',
            summary=summary,
            failing_urls=failing_urls,
            all_health=all_health
        )


@app.route('/api/job/<job_id>/status', methods=['POST'])
def update_job_status(job_id):
    """Update job application status via API."""
    status = request.json.get('status')
    notes = request.json.get('notes', '')
    
    with get_db_context() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not job:
            return jsonify({"error": "Job not found"}), 404
        
        job.application_status = status
        if status == 'applied' and not job.applied_at:
            job.applied_at = datetime.now()
        
        if notes:
            job.notes = notes
        
        db.commit()
        
        return jsonify({"success": True, "status": status})


@app.route('/api/stats')
def stats_api():
    """Get dashboard statistics as JSON."""
    with get_db_context() as db:
        stats = {
            "total_jobs": db.query(Job).filter(Job.is_active == True).count(),
            "new_today": db.query(Job).filter(
                Job.first_seen_at >= datetime.now() - timedelta(days=1)
            ).count(),
            "new_week": db.query(Job).filter(
                Job.first_seen_at >= datetime.now() - timedelta(days=7)
            ).count(),
            "companies": db.query(Job.company).distinct().count(),
            "applied": db.query(Job).filter(Job.application_status == 'applied').count(),
            "interviewing": db.query(Job).filter(Job.application_status == 'interviewing').count(),
        }
        
        return jsonify(stats)


@app.route('/export')
def export_jobs():
    """Export jobs to CSV."""
    import csv
    from io import StringIO
    from flask import Response
    
    with get_db_context() as db:
        jobs = db.query(Job).filter(Job.is_active == True).all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Company', 'Title', 'Location', 'Remote', 'Category',
            'Posted At', 'URL', 'Application Status'
        ])
        
        # Write data
        for job in jobs:
            writer.writerow([
                job.company,
                job.title,
                job.location or '',
                'Yes' if job.remote else 'No',
                job.category or '',
                job.posted_at.strftime('%Y-%m-%d') if job.posted_at else '',
                job.url,
                job.application_status or 'not_applied'
            ])
        
        output.seek(0)
        
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=jobs.csv'}
        )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
