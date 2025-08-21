import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers

from .serializers import ScoreRequestSerializer, ScoreResponseSerializer
from .models import ScoreResult
from .ats_core import compute_score

class ScoreView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, *args, **kwargs):
        ser = ScoreRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        job_title = ser.validated_data["job_title"]
        job_desc = ser.validated_data["job_desc"]
        resume_file = ser.validated_data["resume"]
        use_llm = ser.validated_data.get("use_llm", False)

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        save_path = os.path.join(settings.MEDIA_ROOT, resume_file.name)
        with open(save_path, "wb") as f:
            for chunk in resume_file.chunks():
                f.write(chunk)

        result = compute_score(
            job_title=job_title,
            jd_text=job_desc,
            resume_path=save_path,
            skills_path=os.path.join(settings.BASE_DIR, "skills_ontology.yaml"),
            weights=settings.ATS_WEIGHTS,
            use_llm=use_llm or settings.ATS_ENABLE_LLM,
            llm_model_name=settings.ATS_LLM_MODEL,
        )

        obj = ScoreResult.objects.create(
            job_title=job_title,
            score=result["score"],
            breakdown=result["breakdown"],
            matched_skills=result["matched_skills"],
            hygiene_checks=result["hygiene_checks"],
            notes=result["notes"],
        )

        payload = {
            "id": obj.id,
            "job_title": obj.job_title,
            "score": obj.score,
            "breakdown": obj.breakdown,
            "matched_skills": obj.matched_skills,
            "hygiene_checks": obj.hygiene_checks,
            "notes": obj.notes,
            "created_at": obj.created_at,
        }
        return Response(ScoreResponseSerializer(payload).data, status=status.HTTP_200_OK)
