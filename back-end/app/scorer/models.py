from django.db import models
class ScoreResult(models.Model):
    job_title = models.CharField(max_length=256)
    score = models.FloatField()
    breakdown = models.JSONField()
    matched_skills = models.JSONField(default=list)
    hygiene_checks = models.JSONField(default=dict)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.job_title} ({self.score})"
