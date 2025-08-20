from rest_framework import serializers
class ScoreRequestSerializer(serializers.Serializer):
    job_title = serializers.CharField(max_length=256)
    job_desc = serializers.CharField()
    resume = serializers.FileField()
    use_llm = serializers.BooleanField(required=False, default=False)
class ScoreResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    job_title = serializers.CharField()
    score = serializers.FloatField()
    breakdown = serializers.DictField()
    matched_skills = serializers.ListField(child=serializers.CharField())
    hygiene_checks = serializers.DictField()
    notes = serializers.CharField()
    created_at = serializers.DateTimeField()
