"""
ClaimProcessor -- claim verification workflow, priority scoring, and
status management for the Smart Campus Lost & Found System.

Author: Vikas Reddy Amanagantti (x25178849)
"""

from datetime import datetime, timezone


class ClaimProcessor:
    """
    Manages the lifecycle of item claims: validation, priority scoring,
    status transitions, and approval logic.
    """

    # Allowed status transitions
    VALID_TRANSITIONS = {
        "pending": ["under_review", "approved", "rejected", "withdrawn"],
        "under_review": ["approved", "rejected", "withdrawn"],
        "approved": ["closed"],
        "rejected": [],
        "withdrawn": [],
        "closed": [],
    }

    # Weights for priority scoring
    PRIORITY_WEIGHTS = {
        "evidence_provided": 30,
        "description_length": 20,
        "matching_category": 15,
        "matching_location": 15,
        "timeliness": 20,
    }

    def __init__(self):
        """Initialise the claim processor with an empty claims register."""
        self._claims = {}
        self._audit_log = []

    # ------------------------------------------------------------------
    # Claim lifecycle
    # ------------------------------------------------------------------

    def register_claim(self, claim_id, item_id, claimant_id, description, evidence=None):
        """
        Register a new claim and assign it an initial priority score.

        Args:
            claim_id: Unique claim identifier.
            item_id: The item being claimed.
            claimant_id: The user making the claim.
            description: Textual justification for the claim.
            evidence: Optional supporting evidence string.

        Returns:
            The claim dict including the computed priority.
        """
        claim = {
            "claim_id": claim_id,
            "item_id": item_id,
            "claimant_id": claimant_id,
            "description": description,
            "evidence": evidence,
            "status": "pending",
            "priority": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        claim["priority"] = self.compute_priority(claim)
        self._claims[claim_id] = claim
        self._log_action(claim_id, "registered", "pending")
        return claim

    def compute_priority(self, claim, item=None):
        """
        Compute a priority score (0-100) for a claim based on multiple
        signals: evidence presence, description quality, category match,
        location match, and timeliness.

        Args:
            claim: The claim dict.
            item: Optional item dict for category/location matching.

        Returns:
            An integer priority score between 0 and 100.
        """
        score = 0

        # Evidence bonus
        if claim.get("evidence") and len(claim["evidence"]) > 10:
            score += self.PRIORITY_WEIGHTS["evidence_provided"]

        # Description quality (longer is generally more detailed)
        desc = claim.get("description", "")
        if len(desc) > 100:
            score += self.PRIORITY_WEIGHTS["description_length"]
        elif len(desc) > 50:
            score += self.PRIORITY_WEIGHTS["description_length"] // 2

        # Category and location matching (if item data is available)
        if item:
            if claim.get("category") == item.get("category"):
                score += self.PRIORITY_WEIGHTS["matching_category"]
            if claim.get("location") == item.get("location"):
                score += self.PRIORITY_WEIGHTS["matching_location"]

        # Timeliness -- claims made sooner get higher priority
        score += self.PRIORITY_WEIGHTS["timeliness"]  # baseline; could decay

        return min(score, 100)

    def transition_status(self, claim_id, new_status):
        """
        Attempt to move a claim to a new status.

        Args:
            claim_id: The claim to update.
            new_status: The desired new status string.

        Returns:
            The updated claim dict.

        Raises:
            ValueError: If the transition is not permitted.
            KeyError: If the claim does not exist.
        """
        claim = self._claims.get(claim_id)
        if claim is None:
            raise KeyError(f"Claim {claim_id} not found")

        current = claim["status"]
        allowed = self.VALID_TRANSITIONS.get(current, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition from '{current}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )

        old_status = claim["status"]
        claim["status"] = new_status
        claim["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._log_action(claim_id, f"status_change:{old_status}->{new_status}", new_status)
        return claim

    def approve_claim(self, claim_id):
        """Approve a pending or under-review claim."""
        return self.transition_status(claim_id, "approved")

    def reject_claim(self, claim_id):
        """Reject a pending or under-review claim."""
        return self.transition_status(claim_id, "rejected")

    def withdraw_claim(self, claim_id):
        """Allow a claimant to withdraw their claim."""
        return self.transition_status(claim_id, "withdrawn")

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_claim(self, claim_id):
        """Return a claim dict or None."""
        return self._claims.get(claim_id)

    def get_claims_for_item(self, item_id):
        """Return all claims for a specific item, sorted by priority descending."""
        claims = [c for c in self._claims.values() if c["item_id"] == item_id]
        claims.sort(key=lambda c: c["priority"], reverse=True)
        return claims

    def get_pending_claims(self):
        """Return all claims with status 'pending'."""
        return [c for c in self._claims.values() if c["status"] == "pending"]

    def validate_claim(self, claim):
        """
        Run basic validation on a claim dict.

        Args:
            claim: dict with at least 'description' and 'item_id'.

        Returns:
            A tuple (is_valid: bool, errors: list[str]).
        """
        errors = []
        if not claim.get("description") or len(claim["description"]) < 10:
            errors.append("Description must be at least 10 characters")
        if not claim.get("item_id"):
            errors.append("item_id is required")
        if not claim.get("claimant_id"):
            errors.append("claimant_id is required")
        return (len(errors) == 0, errors)

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def _log_action(self, claim_id, action, status):
        """Append an entry to the internal audit log."""
        self._audit_log.append({
            "claim_id": claim_id,
            "action": action,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_audit_log(self, claim_id=None):
        """
        Retrieve audit log entries, optionally filtered by claim_id.

        Args:
            claim_id: If provided, only return entries for this claim.

        Returns:
            A list of audit log dicts.
        """
        if claim_id is not None:
            return [e for e in self._audit_log if e["claim_id"] == claim_id]
        return list(self._audit_log)
