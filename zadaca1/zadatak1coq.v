Require Import Omega.

Goal forall X Y, ~ (X /\ Y) \/ (~X /\ Y) \/ (~X /\ ~Y) <-> ~(X /\ Y).
Proof.
  intros. split.
  - intros. destruct H.
  -- apply H.
  -- destruct H.
  --- unfold not. intros. destruct H. destruct H0. contradiction.
  --- destruct H. unfold not. intros. apply H. destruct H1. apply H1.
  - intros. left. apply H.
Qed.

Goal forall X Y Z, ~(~X /\ Y /\ ~Z) /\ ~(X /\ Y /\ Z) /\ (X /\ ~Y /\ ~Z) <-> X /\ ~ Y /\ ~ Z.
Proof.
  intros. split.
  - intros. destruct H. destruct H0. destruct H1. destruct H2. split.
  -- apply H1.
  -- split.
  --- apply H2.
  --- apply H3.
  - intros. destruct H. destruct H0. split.
  -- unfold not. intros. destruct H2. destruct H3. apply H4. contradiction.
  -- split. 
  --- unfold not. intros. destruct H2. destruct H3. apply H1. apply H4.
  --- intros. split.
  ---- apply H.
  ---- split.
  ----- apply H0.
  ----- apply H1.
Qed.