function [l, u, pr, pc, r] = zad2(input)
  % returns numbers which satisfy equation l*u = pr*r*input*pc
  m_size = max(size(input));
  
  max_log10 = floor(max(max(log10(input))));
  r = zeros(m_size);
  for i = 1:m_size
    row_max_log10 = floor(max(log10(input(i,:))));
    r(i,i) = 10.^(max_log10 - row_max_log10);
    input(i,:) = input(i,:) * r(i,i);
  end
  
  rows_perm = eye(m_size);
  cols_perm = eye(m_size);
  for i = 1:(m_size - 1)
    max_element = max(max(abs(input(i:m_size, i:m_size))));
    [rows_max, cols_max] = find(abs(input(i:m_size, i:m_size)) == max_element);
    row_max = rows_max(1) + i - 1;
    col_max = cols_max(1) + i - 1;
    if (i != row_max)
      % echanging row max with i-th row
      tmp_p = rows_perm(i,:);
      tmp = input(i,:);
      rows_perm(i,:) = rows_perm(row_max,:);
      input(i,:) = input(row_max,:);
      rows_perm(row_max,:) = tmp_p;
      input(row_max,:) = tmp;
    end
    if (i != col_max)
      % exchanging col max with i-th col
      tmp_p = cols_perm(:,i);
      tmp = input(:,i);
      cols_perm(:,i) = cols_perm(:,col_max);
      input(:,i) = input(:,col_max);
      cols_perm(:,col_max) = tmp_p;
      input(:,col_max) = tmp;
    end
    for j = (i+1):m_size
      input(j,i) /= input(i,i);
    end
    for j = (i+1):m_size
      for k = (i+1):m_size
        input(j,k) -= input(j,i)*input(i,k);
      end
    end
  end
  l = tril(input, -1) + eye(m_size);
  u = triu(input);
  pr = rows_perm;
  pc = cols_perm;
end
