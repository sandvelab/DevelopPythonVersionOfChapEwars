"""chapkit service definition for the Python translation of the CHAP-EWARS model.

Mirrors the R original's main.py (chap-models/chapkit_ewars_model @ 964eea8b): the same
config schema, the same data contract and output, the same runner type. Only the commands
the runner executes, the service id (with a -python suffix) and the descriptive metadata
differ, so chap-core drives both models the same way.
"""

import os
from pathlib import Path

from chapkit import BaseConfig
from chapkit.api import AssessedStatus, MLServiceBuilder, MLServiceInfo, ModelMetadata, PeriodType
from chapkit.artifact import ArtifactHierarchy
from chapkit.ml import ShellModelRunner
from pydantic import Field


class EwarsConfig(BaseConfig):
    prediction_periods: int = Field(
        default=3,
        description="Number of periods to predict into the future",
    )
    n_lags: list[int] = Field(
        default_factory=lambda: [3],
        description=(
            "Number of lags per covariate, in the same order as "
            "additional_continuous_covariates. A single-element list "
            "broadcasts to all covariates."
        ),
    )
    precision: float = Field(
        default=0.01,
        description="Prior on the precision of fixed effects. Works as regularization",
    )
    region_seasonal: bool = Field(
        default=False,
        description="Optional inclusion of region specific seasonal effects",
    )
    additional_continuous_covariates: list[str] = Field(
        default_factory=lambda: ["rainfall", "mean_temperature"],
        description=(
            "Continuous covariates to include as lagged predictors in the model. "
            "Defaults match the legacy CHAP-EWARS model which used rainfall and "
            "mean_temperature. Override via POST /api/v1/configs to run with a "
            "different covariate set."
        ),
    )


runner: ShellModelRunner[EwarsConfig] = ShellModelRunner(
    train_command="python scripts/train.py --data {data_file}",
    predict_command=(
        "python scripts/predict.py --historic {historic_file} --future {future_file} --output {output_file}"
    ),
)

info = MLServiceInfo(
    id="chapkit-ewars-model-python",
    display_name="CHAP-EWARS Model (chapkit, Python)",
    version="0.1.0",
    description=(
        "Python translation of the chapkit CHAP-EWARS model: the same Bayesian hierarchical "
        "negative-binomial model with distributed-lag climate covariates, with dlnmpy in place of "
        "R dlnm and an INLA-style Laplace approximation written in Python in place of R-INLA. "
        "Modified version of the World Health Organization (WHO) EWARS model."
    ),
    model_metadata=ModelMetadata(
        author="CHAP team (R original); Python translation",
        author_assessed_status=AssessedStatus.orange,
        organization="HISP Centre, University of Oslo",
        organization_logo_url="https://landportal.org/sites/default/files/2024-03/university_of_oslo_logo.png",
        contact_email="knut.rand@dhis2.org",
        citation_info=(
            'Climate Health Analytics Platform. 2025. "CHAP-EWARS model". '
            "HISP Centre, University of Oslo. "
            "https://dhis2-chap.github.io/chap-core/external_models/overview_of_supported_models.html"
        ),
    ),
    period_type=PeriodType.any,
    allow_free_additional_continuous_covariates=True,
    required_covariates=["population"],
    min_prediction_periods=0,
    max_prediction_periods=100,
)

hierarchy = ArtifactHierarchy(
    name="ewars",
    level_labels={0: "ml_training_workspace", 1: "ml_prediction"},
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/chapkit.db")
if DATABASE_URL.startswith("sqlite") and ":///" in DATABASE_URL:
    db_path = Path(DATABASE_URL.split("///")[1])
    db_path.parent.mkdir(parents=True, exist_ok=True)

app = (
    MLServiceBuilder(
        info=info,
        config_schema=EwarsConfig,
        hierarchy=hierarchy,
        runner=runner,
        database_url=DATABASE_URL,
    )
    .with_monitoring()
    .with_registration(keepalive_interval=15)
    .build()
)
