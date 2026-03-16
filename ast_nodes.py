"""
KUCODE AST Node Definitions
============================
Dataclass-based AST nodes for the KUCODE compiler.
Built by the LL(1) table-driven parser, walked by the semantic analyzer.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List


# ═══════════════════════════════════════════════════════════════
# BASE CLASSES
# ═══════════════════════════════════════════════════════════════

@dataclass
class ASTNode:
    line: int = 0
    col: int = 0


@dataclass
class Expr(ASTNode):
    pass


@dataclass
class Stmt(ASTNode):
    pass


# ═══════════════════════════════════════════════════════════════
# PROGRAM STRUCTURE
# ═══════════════════════════════════════════════════════════════

@dataclass
class Program(ASTNode):
    groups: List[GroupDef] = field(default_factory=list)
    worldwide_decls: List[WorldwideDecl] = field(default_factory=list)
    functions: List[FuncDef] = field(default_factory=list)
    start_body: List[Stmt] = field(default_factory=list)


@dataclass
class GroupDef(ASTNode):
    name: str = ''
    members: List[GroupMember] = field(default_factory=list)


@dataclass
class GroupMember(ASTNode):
    datatype: str = ''
    name: str = ''


@dataclass
class WorldwideDecl(ASTNode):
    is_fixed: bool = False
    datatype: str = ''
    name: str = ''
    value: Optional[Expr] = None


@dataclass
class FuncDef(ASTNode):
    return_type: str = ''
    name: str = ''
    params: List[Parameter] = field(default_factory=list)
    local_decls: List[Stmt] = field(default_factory=list)
    body: List[Stmt] = field(default_factory=list)
    return_stmt: Optional[ReturnStmt] = None


@dataclass
class Parameter(ASTNode):
    datatype: str = ''
    name: str = ''


# ═══════════════════════════════════════════════════════════════
# DECLARATIONS (Stmt)
# ═══════════════════════════════════════════════════════════════

@dataclass
class VarDecl(Stmt):
    datatype: str = ''
    name: str = ''
    value: Optional[Expr] = None
    is_group_typed: bool = False


@dataclass
class FixedDecl(Stmt):
    datatype: str = ''
    name: str = ''
    value: Optional[Expr] = None


@dataclass
class ListDecl(Stmt):
    datatype: str = ''
    name: str = ''
    value: Optional[ListLiteral1D | ListLiteral2D] = None


# ═══════════════════════════════════════════════════════════════
# STATEMENTS (Stmt)
# ═══════════════════════════════════════════════════════════════

@dataclass
class Assignment(Stmt):
    target: Optional[Expr] = None
    value: Optional[Expr] = None


@dataclass
class CompoundAssign(Stmt):
    op: str = ''
    target: Optional[Expr] = None
    value: Optional[Expr] = None


@dataclass
class Increment(Stmt):
    target: Optional[Expr] = None


@dataclass
class Decrement(Stmt):
    target: Optional[Expr] = None


@dataclass
class IfChain(Stmt):
    condition: Optional[Expr] = None
    body: List[Stmt] = field(default_factory=list)
    elif_branches: List[ElifBranch] = field(default_factory=list)
    else_body: Optional[List[Stmt]] = None


@dataclass
class ElifBranch(ASTNode):
    condition: Optional[Expr] = None
    body: List[Stmt] = field(default_factory=list)


@dataclass
class SelectStmt(Stmt):
    variable: str = ''
    options: List[OptionBlock] = field(default_factory=list)
    fallback: Optional[List[Stmt]] = None


@dataclass
class OptionBlock(ASTNode):
    value: Optional[Expr] = None
    body: List[Stmt] = field(default_factory=list)
    control_flow: str = 'stop'


@dataclass
class EachLoop(Stmt):
    variable: str = ''
    from_expr: Optional[Expr] = None
    to_expr: Optional[Expr] = None
    step_expr: Optional[Expr] = None
    body: List[Stmt] = field(default_factory=list)


@dataclass
class DuringLoop(Stmt):
    condition: Optional[Expr] = None
    body: List[Stmt] = field(default_factory=list)


@dataclass
class FuncCallStmt(Stmt):
    call: Optional[FuncCall] = None


@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr] = None


@dataclass
class ShowStmt(Stmt):
    args: List[Expr] = field(default_factory=list)


@dataclass
class DisplayStmt(Stmt):
    args: List[Expr] = field(default_factory=list)


@dataclass
class ReadStmt(Stmt):
    variable: str = ''


# ═══════════════════════════════════════════════════════════════
# EXPRESSIONS (Expr)
# ═══════════════════════════════════════════════════════════════

@dataclass
class BinaryOp(Expr):
    op: str = ''
    left: Optional[Expr] = None
    right: Optional[Expr] = None


@dataclass
class UnaryOp(Expr):
    op: str = ''
    operand: Optional[Expr] = None


@dataclass
class Literal(Expr):
    token_type: str = ''
    value: str = ''


@dataclass
class Identifier(Expr):
    name: str = ''


@dataclass
class FuncCall(Expr):
    name: str = ''
    args: List[Expr] = field(default_factory=list)


@dataclass
class ListAccess(Expr):
    name: str = ''
    index1: Optional[Expr] = None
    index2: Optional[Expr] = None


@dataclass
class MemberAccess(Expr):
    object_name: str = ''
    member: str = ''


@dataclass
class SizeCall(Expr):
    list_name: str = ''
    dimension: Optional[str] = None


@dataclass
class ListLiteral1D(Expr):
    elements: List[Expr] = field(default_factory=list)


@dataclass
class ListLiteral2D(Expr):
    rows: List[ListLiteral1D] = field(default_factory=list)
