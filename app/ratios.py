def dekking_cf_vv(cf, vv) -> float:
        """Dekking van langetermijnschulden door cashflow."""
        score = cf / vv
        
        return score

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
    
def solvabiliteitsscore(ev, tv):
     solvabiliteitsscore = ev / tv
     return solvabiliteitsscore