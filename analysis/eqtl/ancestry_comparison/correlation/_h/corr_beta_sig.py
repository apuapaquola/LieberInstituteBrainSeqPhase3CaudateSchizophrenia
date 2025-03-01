"""
This script examines the Spearman correlation of beta (slope) between
ancestries.

This uses significant SNP-gene pairs.
"""
import functools
import pandas as pd
from scipy.stats import spearmanr
from rpy2.robjects.packages import importr
from rpy2.robjects import r, globalenv, pandas2ri

@functools.lru_cache()
def load_beta(label):
    label_dict = {"aa_only": "AA", "ea_only":"EA", "all": "ALL"}
    fn ="/ceph/projects/v4_phase3_paper/analysis/eqtl_analysis/"+\
        "%s/genes/expression_gct/prepare_expression/" % label+\
        "annotate_outputs/_m/Brainseq_LIBD.signifpairs.txt.gz"
    return pd.read_csv(fn, sep='\t', usecols=[0,1,7])\
             .rename(columns={"slope":label_dict[label]})


@functools.lru_cache()
def prepare_data():
    aa = load_beta("aa_only")
    ea = load_beta("ea_only")
    eqtl = load_beta("all")
    return aa, ea, eqtl


@functools.lru_cache()
def merge_data():
    aa, ea, eqtl = prepare_data()
    return pd.merge(aa, ea, on=["gene_id", "variant_id"])\
             .merge(eqtl, on=["gene_id", "variant_id"])


def corr_beta(df, label1, label2):
    return spearmanr(df[label1], df[label2])


def plotNsave_corr(df):
    #ggpubr = importr('ggpubr')
    pandas2ri.activate()
    globalenv['df'] = df
    r('''
    pp1 = ggpubr::ggscatter(df, x="ALL", y="AA", add="reg.line", size=1,
                            xlab="eQTL beta (ALL)", ylab="eQTL beta (AA)",
                            add.params=list(color="blue", fill="lightgray"),
                            conf.int=TRUE, cor.coef=TRUE, cor.coef.size=3,
                            cor.method="spearman", cor.coeff.args=list(label.sep="\n"),
                            ggtheme=ggpubr::theme_pubr(base_size=15))
    pp2 = ggpubr::ggscatter(df, x="ALL", y="EA", add="reg.line", size=1,
                            xlab="eQTL beta (ALL)", ylab="eQTL beta (EA)",
                            add.params=list(color="blue", fill="lightgray"),
                            conf.int=TRUE, cor.coef=TRUE, cor.coef.size=3,
                            cor.method="spearman", cor.coeff.args=list(label.sep="\n"),
                            ggtheme=ggpubr::theme_pubr(base_size=15))
    pp3 = ggpubr::ggscatter(df, x="AA", y="EA", add="reg.line", size=1,
                            xlab="eQTL beta (AA)", conf.int=TRUE,
                            ylab="eQTL beta (EA)", cor.coef=TRUE,
                            cor.coef.size=3, cor.method="spearman",
                            cor.coeff.args=list(label.sep="\n"),
                            add.params=list(color="blue", fill="lightgray"),
                            ggtheme=ggpubr::theme_pubr(base_size=15))
    figure = ggpubr::ggarrange(pp1, pp2, pp3, ncol=3, nrow=1, align='v')
    ggplot2::ggsave(plot=figure, dpi=72, width=9, height=3,
                    filename="scatter_slope_ancestry_eqtl_sig.pdf")
    ggplot2::ggsave(plot=figure, dpi=300, width=9, height=3,
                    filename="scatter_slope_ancestry_eqtl_sig.png")
    ''')


def main():
    ## Load data
    df = merge_data()
    ## Calculate rho
    with open("rho_statistics_sig.log", "w") as f:
        rho1, pval1 = corr_beta(df, "ALL", "AA")
        print("rho between ALL and AA:\t\t %.3f" % rho1, file=f)
        rho2, pval2 = corr_beta(df, "ALL", "EA")
        print("rho between ALL and EA:\t\t %.3f" % rho2, file=f)
        rho3, pval3 = corr_beta(df, "AA", "EA")
        print("rho between ancestries (AA vs EA):\t %.3f" % rho3, file=f)
    ## Generate figure
    plotNsave_corr(df)


if __name__ == "__main__":
    main()
