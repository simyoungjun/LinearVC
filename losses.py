import torch 
from torch.nn import functional as F

from utils import commons


def feature_loss(fmap_r, fmap_g):
  loss = 0
  for dr, dg in zip(fmap_r, fmap_g):
    for rl, gl in zip(dr, dg):
      rl = rl.float().detach()
      gl = gl.float()
      loss += torch.mean(torch.abs(rl - gl))

  return loss * 2 


def discriminator_loss(disc_real_outputs, disc_generated_outputs):
  loss = 0
  r_losses = []
  g_losses = []
  for dr, dg in zip(disc_real_outputs, disc_generated_outputs):
    dr = dr.float()
    dg = dg.float()
    r_loss = torch.mean((1-dr)**2)
    g_loss = torch.mean(dg**2)
    loss += (r_loss + g_loss)
    r_losses.append(r_loss.item())
    g_losses.append(g_loss.item())

  return loss, r_losses, g_losses


def generator_loss(disc_outputs):
  loss = 0
  gen_losses = []
  for dg in disc_outputs:
    dg = dg.float()
    l = torch.mean((1-dg)**2)
    gen_losses.append(l)
    loss += l

  return loss, gen_losses


def kl_loss(z_p, logs_q, m_p, logs_p, z_mask):
  """
  z_p, logs_q: [b, h, t_t]
  m_p, logs_p: [b, h, t_t]
  """
  z_p = z_p.float()
  logs_q = logs_q.float()
  m_p = m_p.float()
  logs_p = logs_p.float()
  z_mask = z_mask.float()
  #print(logs_p)
  kl = logs_p - logs_q - 0.5
  kl += 0.5 * ((z_p - m_p)**2) * torch.exp(-2. * logs_p)
  kl = torch.sum(kl * z_mask)
  l = kl / torch.sum(z_mask)
  return l

def vq_loss(x, quantized, commitment_labmda=0.25, codebook_labmda=1, posterior_emb=None):
  #detach()로 codebook 은 gradient update하지 않고, encoder만 codebook에 가까울 수 있게 update
  # codebook loss 없는 버전
  encoder_latent_loss = F.mse_loss(x, quantized.detach())
  commitment_loss = commitment_labmda * encoder_latent_loss
  
  # codebook loss 있는 버전
  if codebook_labmda == 0:
    codebook_loss = torch.tensor([0])
  else:
    if posterior_emb == None:
      codebook_loss = F.mse_loss(x.detach(), quantized) #latent_loss
    else:
      codebook_loss = F.mse_loss(posterior_emb.detach(), quantized)
      
  return commitment_loss, codebook_loss

