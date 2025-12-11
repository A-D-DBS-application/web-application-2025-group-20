def cf_coverage_ratio(self) -> float:
        """Dekking van langetermijnschulden door cashflow."""
        score = (self.cash_flow - self.cash) / self.long_term_debt
        if self.long_term_debt:
            return score
        else:
            return 0.0

def net_financial_leverage(self) -> float:
    """Netto financiële schuldgraad."""
    score = (self.debt - self.cash) / self.equity
    if self.equity:
        return score
    else:
        return 0.0

def long_term_independence(self) -> float:
        """Langetermijngraad van financiële onafhankelijkheid."""
         
        denom = self.long_term_debt + self.equity
        score = self.equity / denom
        if denom:
            score
        else:
            return 0.0

def ebitda_multiplier(self) -> float:
    """EBITDA multiplicator."""
    score = self.debt/self.ebitda
    if self.ebitda:
        return score
    else:
        return 0.0
    
def schuldgraad(vv, tv):
     schuldgraad = vv / tv
     return schuldgraad