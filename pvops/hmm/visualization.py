import matplotlib.pyplot as plt

def observe_timeseries_plot(prod_df, mask=None, npts=None, site=None):
    prod_df = prod_df.copy()
    
    try:
        print(f"Mask captures {sum(mask)} of {len(prod_df)} rows")
    except:
        pass
    prod_df['mask'] = mask

    # Subset site
    if not isinstance(site, type(None)):
        prod_df_visualize = prod_df[prod_df['randid'] == site]
    else:
        prod_df_visualize = prod_df
    if not isinstance(npts, type(None)):
        prod_df_visualize = prod_df_visualize.iloc[0:npts]
    # Subset to mask
    if not isinstance(mask, type(None)):
        prod_df_visualize = prod_df_visualize[prod_df_visualize['mask']==True]

    fig, (ax, ax2) = plt.subplots(2, figsize=(12,6))
    
    ax.plot(prod_df_visualize.index, prod_df_visualize["measured_expected_ratio"], "k--", alpha=0.4)
    ax.set_ylabel("Measured Energy / Expected Energy")

    ax2.plot(prod_df_visualize.index, prod_df_visualize['energy_generated_kWh'], "k--", alpha=0.4)
    ax2.set_ylabel("Energy Generated (kWh)")
    plt.show()

    return fig, (ax, ax2)

def observe_energy_vs_irradiance(prod_df, prod_col_dict, mask=None):
    prod_df = prod_df.copy()
    
    try:
        print(f"Mask captures {sum(mask)} of {len(prod_df)} rows")
    except:
        pass
    
    # Subset to mask
    if not isinstance(mask, type(None)):
        prod_df_visualize = prod_df.loc[mask]
    else:
        prod_df_visualize = prod_df
    fig, ax = plt.subplots(1, figsize=(8,8))
    sc = ax.scatter(prod_df_visualize[prod_col_dict['irradiance']], prod_df_visualize[prod_col_dict['energyprod']], c=prod_df_visualize['capacity'])
    cbar = plt.colorbar(sc)
    cbar.ax.set_label('System capacity (kWh)')
    ax.set_ylabel('Energy production (kWh)')
    ax.set_xlabel('Irradiance (W/m2)')
    plt.show()

    return fig, ax